# AIAgentForge/state/document_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState
import os
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient
import asyncio
from supabase import create_client, Client
import io # For handling file bytes

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
BUCKET_NAME = "document-files"
DOCUMENT_TABLE = "documents"

class DocumentState(BaseState):
    """특정 컬렉션의 문서 관리와 관련된 상태 및 로직을 처리합니다."""
    
    documents: list[dict] = []
    is_loading: bool = False
    is_uploading: bool = False
    
    upload_progress: dict[str, int] = {}
    upload_status: dict[str, str] = {}
    upload_errors: dict[str, str] = {}
    
    show_alert: bool = False
    alert_message: str = ""

    async def _get_authenticated_client(self) -> SyncPostgrestClient:
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            raise Exception("사용자가 인증되지 않았습니다.")
        return SyncPostgrestClient(
            f"{SUPABASE_URL}/rest/v1",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {auth_state.access_token}",
            }
        )

    async def _get_supabase_client(self) -> Client:
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            raise Exception("사용자가 인증되지 않았습니다.")
        client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.auth.set_session(auth_state.access_token, '')
        return client

    async def load_documents_on_page_load(self):
        collection_id = self.router.page.params.get("collection_id")
        if not collection_id:
            self.alert_message = "컬렉션 ID를 찾을 수 없습니다."
            self.show_alert = True
            return

        self.is_loading = True
        yield
        try:
            client = await self._get_authenticated_client()
            response = client.from_("documents").select("*").eq("collection_id", collection_id).execute()
            self.documents = response.data
        except Exception as e:
            self.alert_message = f"문서 로딩 실패: {e}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield

    async def handle_upload(self, files: list[rx.UploadFile]):
        """업로드된 파일들을 처리하며 단계별로 상태를 직접 업데이트합니다."""
        collection_id = self.router.page.params.get("collection_id")
        if not collection_id:
            self.alert_message = "컬렉션이 지정되지 않았습니다."
            self.show_alert = True
            return

        if not files:
            return

        self.is_uploading = True
        for file in files:
            filename = file.name
            self.upload_status[filename] = "대기 중..."
            self.upload_progress[filename] = 0
            self.upload_errors.pop(filename, None)
        yield

        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            self.alert_message = "사용자를 찾을 수 없습니다."
            self.show_alert = True
            self.is_uploading = False
            return

        successful_uploads = 0
        supabase_client = await self._get_supabase_client()
        for file in files:
            filename = file.name
            try:
                self.upload_status[filename] = "처리 중..."
                self.upload_progress[filename] = 33
                yield

                upload_data = await file.read()
                
                self.upload_status[filename] = "스토리지에 업로드 중..."
                self.upload_progress[filename] = 66
                yield

                storage_response = supabase_client.storage.from_('document-files').upload(
                    f"{auth_state.user.id}/{filename}",  # 변경: collection_id → auth_state.user.id (UUID)
                    upload_data,
                    {'content-type': file.content_type or 'application/octet-stream'}
                )

                # # *** 중요: 버킷 이름을 'document-files'로 변경 (밑줄(_) 대신 하이픈(-) 사용) ***
                # storage_response = supabase_client.storage.from_('document-files').upload(
                #     f"{collection_id}/{filename}",
                #     upload_data,
                #     {'content-type': file.content_type or 'application/octet-stream'}
                # )
                if not storage_response.full_path:
                    # Supabase 스토리지 응답이 JSON 형태일 수 있으므로 텍스트로 변환
                    error_detail = storage_response.text
                    raise Exception(f"Storage upload failed: {error_detail}")

                db_client = await self._get_authenticated_client()
                db_client.from_("documents").insert({
                    "name": filename,
                    "collection_id": collection_id,
                    "owner_id": auth_state.user.id,
                    "storage_path": storage_response.full_path
                }).execute()
                
                self.upload_status[filename] = "✅ 완료"
                self.upload_progress[filename] = 100
                successful_uploads += 1
                yield
                
            except Exception as e:
                self.upload_status[filename] = "❌ 실패"
                self.upload_errors[filename] = f"오류: {str(e)}"
                self.upload_progress[filename] = 100
                yield
                
        if successful_uploads > 0:
            self.alert_message = f"{successful_uploads} / {len(files)}개의 파일이 성공적으로 업로드되었습니다."
            self.show_alert = True
            # 컬렉션 상세 페이지에 문서 목록이 있다면 새로고침
            # yield DocumentState.load_documents_on_page_load
        
        await asyncio.sleep(5)
        self.is_uploading = False
        self.upload_progress = {}
        self.upload_status = {}
        self.upload_errors = {}
        yield


    async def delete_document(self, doc_id: str):
        """문서를 삭제합니다: 스토리지에서 파일 삭제 후 DB에서 레코드 삭제."""
        self.is_loading = True  # 로딩 상태 설정 (선택적)
        yield

        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                raise Exception("사용자를 찾을 수 없습니다.")

            db_client = await self._get_authenticated_client()

            # 먼저 문서 정보 가져오기 (storage_path 필요)
            response = db_client.from_("documents").select("storage_path, owner_id").eq("id", doc_id).execute()
            if not response.data:
                raise Exception("문서를 찾을 수 없습니다.")

            doc_data = response.data[0]
            if doc_data["owner_id"] != auth_state.user.id:
                raise Exception("삭제 권한이 없습니다.")

            storage_path = doc_data["storage_path"]

            # 만약 storage_path가 버킷 이름을 포함하고 있다면 제거 (호환성을 위해)
            if storage_path.startswith(f"{BUCKET_NAME}/"):
                path_to_remove = storage_path[len(f"{BUCKET_NAME}/"):]
            else:
                path_to_remove = storage_path

            # 스토리지에서 파일 삭제
            supabase_client = await self._get_supabase_client()
            storage_response = supabase_client.storage.from_(BUCKET_NAME).remove([path_to_remove])
            # 삭제 응답 확인: []이면 삭제되지 않음 (경로가 잘못된 경우)
            if not storage_response:
                raise Exception("스토리지 파일 삭제 실패: 파일을 찾을 수 없음 또는 경로 오류.")

            # DB에서 레코드 삭제
            db_client.from_("documents").delete().eq("id", doc_id).execute()

            # 상태 업데이트: 목록에서 제거
            self.documents = [doc for doc in self.documents if doc["id"] != doc_id]

            self.alert_message = "문서가 성공적으로 삭제되었습니다."
            self.show_alert = True

        except Exception as e:
            self.alert_message = f"문서 삭제 실패: {str(e)}"
            self.show_alert = True

        finally:
            self.is_loading = False
            yield