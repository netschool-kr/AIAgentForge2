# AIAgentForge/state/document_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState
import os
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient
import asyncio
from supabase import create_client, Client
from reflex.vars import Var
from typing import List
from ..utils.text_extractor import extract_text_from_file
from ..utils.chunker import chunk_text
from ..utils.embedder import generate_embeddings
from urllib.parse import parse_qs, quote # quote import 추가
import uuid
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
BUCKET_NAME = "document-files"
DOCUMENT_TABLE = "documents"

class DocumentState(BaseState):
    """특정 컬렉션의 문서 관리와 관련된 상태 및 로직을 처리합니다."""
    
    documents: list[dict] = []
    collection_name: str = ""
    collect_id: str=""
    is_loading: bool = False
    is_uploading: bool = False
    # upload_document: bool = True
    # process_document: bool = True
    upload_progress: dict[str, int] = {}
    upload_status: dict[str, str] = {}
    upload_errors: dict[str, str] = {}

    show_alert: bool = False
    alert_message: str = ""

    def toggle_upload_document(self):
        """upload_document 상태를 토글합니다. (True ↔ False)"""
        self.upload_document = not self.upload_document

    def toggle_process_document(self):
        """process_document 상태를 토글합니다. (True ↔ False)"""
        self.process_document = not self.process_document
        
    def set_process_document(self, value: bool):
        self.process_document = value

    async def load_documents_on_page_load(self):
        logging.info(f"load_documents_on_page_load:{self.router.url}")
        collection_id = self.router.url.split('/')[-1]
        
        if not collection_id:
            self.alert_message = "컬렉션 ID를 찾을 수 없습니다."
            self.show_alert = True
            return

        self.is_loading = True
        self.collection_id = collection_id
        
        yield
        try:
            client = await self._get_authenticated_client()
            
            collection_response = client.from_("collections").select("name").eq("id", collection_id).single().execute()
            if collection_response.data:
                self.collection_name = collection_response.data.get("name", "이름 없음")
            else:
                self.collection_name = "알 수 없는 컬렉션"
                            
            response = client.from_("documents").select("*").eq("collection_id", collection_id).execute()
            self.documents = response.data
        except Exception as e:
            self.alert_message = f"문서 로딩 실패: {e}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield

    # Supabase Bucket에 file을 upload
    async def handle_upload(self, files: list[rx.UploadFile]):
        """업로드된 파일들을 처리하며 단계별로 상태를 직접 업데이트합니다."""
        collection_id = self.router.url.split('/')[-1]
        
        if not collection_id:
            print("컬렉션이 지정되지 않았습니다.")
            self.alert_message = "컬렉션이 지정되지 않았습니다."
            self.show_alert = True
            return

        if not files:
            return
            
        supabase_client = await self._get_supabase_client()

        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            print("사용자를 찾을 수 없습니다.")
            self.alert_message = "사용자를 찾을 수 없습니다."
            self.show_alert = True
            self.is_uploading = False
            return
        user_id = auth_state.user.id
        
        db_client = await self._get_authenticated_client()

        self.is_uploading = True
        
        for file in files:
            filename = file.name
            self.upload_status[filename] = "대기 중..."
            self.upload_progress[filename] = 0
            self.upload_errors.pop(filename, None)
        yield


        successful_uploads = 0
        for file in files:
            original_filename = file.name # [수정] 원래 파일 이름 저장
            try:
                # [수정] DB 중복 체크는 원래 파일 이름으로 수행
                existing_doc_res = db_client.from_("documents").select("id").eq("name", original_filename).eq("collection_id", collection_id).maybe_single().execute()
                
                if existing_doc_res and existing_doc_res.data:
                    logger.warning(f"File '{original_filename}' already exists in this collection. Skipping.")
                    self.upload_status[original_filename] = "❌ 실패"
                    self.upload_errors[original_filename] = "이미 같은 이름의 파일이 존재합니다."
                    self.upload_progress[original_filename] = 100
                    yield
                    continue
                
                file_content = await file.read()
                content_type = file.content_type

                self.upload_status[original_filename] = "스토리지에 업로드 중..."
                self.upload_progress[original_filename] = 10
                yield

                # [수정] 스토리지에 저장할 새 파일 이름 생성 (UUID + 원래 확장자)
                file_extension = os.path.splitext(original_filename)[1]
                storage_filename = f"{uuid.uuid4()}{file_extension}"
                storage_path = f"{user_id}/{collection_id}/{storage_filename}"
                
                logger.info(f"Attempting to upload to storage path: {storage_path}")

                storage_response = supabase_client.storage.from_(BUCKET_NAME).upload(
                    storage_path,
                    file_content,
                    {'content-type': content_type or 'application/octet-stream'}
                )

                if not storage_response.full_path:
                    error_detail = storage_response.text
                    raise Exception(f"Storage upload failed: {error_detail}")

                # [수정] DB에는 원래 파일 이름(name)과 UUID 기반 경로(storage_path)를 함께 저장
                response = db_client.from_("documents").insert({
                    "name": original_filename,
                    "collection_id": collection_id,
                    "owner_id": user_id,
                    "storage_path": storage_response.full_path
                }).execute()

                if response.data:
                    inserted_document = response.data[0]
                    document_id = inserted_document['id']
                    print(f"새로 생성된 문서 ID: {document_id}")
                    
                self.upload_progress[original_filename] = 20
                self.upload_status[original_filename] = "Text 추출 중"
                successful_uploads += 1
                yield
                    
                print(" Process Document")
                
                self.upload_progress[original_filename] = 30                
                self.upload_status[original_filename] = "Text 추출 중"
                yield
                
                text = extract_text_from_file(file_content, content_type)
                logger.info(f"Extracted text length for {original_filename}: {len(text)}")
                if not text:
                    print(f"No text extracted for {original_filename}, content_type: {content_type}")
                    
                self.upload_progress[original_filename] = 50
                self.upload_status[original_filename] = "Chunking"
                yield

                chunks = chunk_text(text)
                logger.info(f"Number of chunks for {original_filename}: {len(chunks)}")
                if not chunks:
                    print(f"No chunks created for {original_filename}")

                self.upload_progress[original_filename] = 60
                self.upload_status[original_filename] = "Embedding"
                yield

                embeddings = await generate_embeddings([chunk['text'] for chunk in chunks])
                logger.info(f"Number of embeddings for {original_filename}: {len(embeddings)}")

                self.upload_progress[original_filename] = 80
                self.upload_status[original_filename] = "DB Updating"
                yield

                logger.info(f"Using document_id: {document_id} for {original_filename}")
                records_to_insert = [
                    {
                        "owner_id": user_id,
                        "document_id": document_id,
                        "content": chunk['text'],
                        "embedding": embedding,
                    }
                    for chunk, embedding in zip(chunks, embeddings)
                ]
                logger.info(f"Number of records to insert for {original_filename}: {len(records_to_insert)}")
                
                
                if records_to_insert:
                    response = supabase_client.table("document_sections").insert(records_to_insert).execute()
                    logger.info(f"Insert response for {original_filename}: data length={len(response.data) if response.data else 0}, count={response.count}")
                else:
                    logger.info(f"No records to insert for {original_filename}")

                self.upload_progress[original_filename] = 100
                self.upload_status[original_filename] = "✅ 완료"

                yield
                    
            except Exception as e:
                self.upload_status[original_filename] = "❌ 실패"
                self.upload_errors[original_filename] = f"오류: {str(e)}"
                self.upload_progress[original_filename] = 100
                yield
                
        if successful_uploads > 0:
            self.alert_message = f"{successful_uploads} / {len(files)}개의 파일이 성공적으로 업로드되었습니다."
            self.show_alert = True
            yield DocumentState.load_documents_on_page_load
        
        await asyncio.sleep(5)
        self.is_uploading = False
        self.upload_progress = {}
        self.upload_status = {}
        self.upload_errors = {}
        yield
                            
    #@rx.event(background=True)
    async def ProcessDocument(self, supabase_client, filename: str, collection_id: str):
        try:

            # async with self:
            #     self.upload_progress[filename] = 0
                

            text = extract_text_from_file(self.file_content, self.content_type)
            logger.info(f"Extracted text length for {filename}: {len(text)}")
            if not text:
                print(f"No text extracted for {filename}, content_type: {self.content_type}")
                
            # async with self:
            #     self.upload_progress[filename] = 25

            chunks = chunk_text(text)
            logger.info(f"Number of chunks for {filename}: {len(chunks)}")
            if not chunks:
                print(f"No chunks created for {filename}")
            async with self:
                self.upload_progress[filename] = 50

            embeddings = await generate_embeddings([chunk['text'] for chunk in chunks])
            logger.info(f"Number of embeddings for {filename}: {len(embeddings)}")
            # async with self:
            #     self.upload_progress[filename] = 75

            logger.info(f"Using collection_id: {collection_id} for {filename}")
            records_to_insert = [
                {
                    "chunk_text": chunk['text'],
                    "embedding": embedding,
                    "document_name": filename,
                    "collection_id": int(collection_id)  # Convert to int for Supabase
                }
                for chunk, embedding in zip(chunks, embeddings)
            ]
            logger.info(f"Number of records to insert for {filename}: {len(records_to_insert)}")
            
            # supabase_client = await self._get_supabase_client()
            
            if records_to_insert:
                response = supabase_client.table("document_sections").insert(records_to_insert).execute()
                logger.info(f"Insert response for {filename}: data length={len(response.data) if response.data else 0}, count={response.count}")
            else:
                logger.info(f"No records to insert for {filename}")
            # async with self:
            #     self.upload_progress[filename] = 100
            #     #del self._upload_data[filename]

        except Exception as e:
            logger.info(f"Error processing {filename}: {str(e)}")
            import traceback
            logger.info(traceback.format_exc())
            async with self:
                self.upload_progress[filename] = -1
                # if filename in self._upload_data:
                #     del self._upload_data[filename]
        logger.info(f"process_document completed for {filename}")

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