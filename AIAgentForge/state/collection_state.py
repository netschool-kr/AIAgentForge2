# AIAgentForge/state/collection_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState  # Assuming AuthState exists and inherits from BaseState
from postgrest import SyncPostgrestClient
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # Anon key for public access, but we'll add bearer token

class CollectionState(BaseState):
    """컬렉션 관리와 관련된 모든 상태와 로직을 중앙에서 관리합니다."""

    # UI를 구동하는 핵심 상태 변수들
    collections: list[dict] = []
    is_loading: bool = False
    new_collection_name: str = ""
    
    # 사용자 피드백을 위한 상태 변수들
    show_alert: bool = False
    alert_message: str = ""


               
    async def _get_authenticated_client(self):
        """Create authenticated Postgrest client with user's token."""
        auth_state = await self.get_state(AuthState)  # Await get_state
        if not auth_state.is_authenticated or not hasattr(auth_state, 'access_token'):
            raise Exception("Not authenticated or no token available")
        return SyncPostgrestClient(
            f"{SUPABASE_URL}/rest/v1",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {auth_state.access_token}",
            }
        )

    def set_new_collection_name(self, value: str):
        """새 컬렉션 이름 상태를 업데이트합니다."""
        self.new_collection_name = value 
        
    async def load_collections(self):
        """사용자 소유의 모든 컬렉션을 데이터베이스에서 불러옵니다."""
        self.is_loading = True
        yield

        try:
            client = await self._get_authenticated_client()
            response = client.from_("collections").select("*").eq("owner_id", self.user.id).order("created_at", desc=True).execute()
            self.collections = response.data
        except Exception as e:
            self.alert_message = f"컬렉션 로딩 실패: {str(e)}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield
    
    async def create_collection(self):
        """새로운 컬렉션을 생성합니다."""
        if not self.new_collection_name.strip():
            self.alert_message = "컬렉션 이름은 비워둘 수 없습니다."
            self.show_alert = True
            yield
            return

        self.is_loading = True
        yield

        success = False
        try:
            client = await self._get_authenticated_client()
            response = client.from_("collections").insert({
                "name": self.new_collection_name,
                "owner_id": self.user.id  # 명시적으로 owner_id 추가
            }).execute()
            
            # 입력 필드 초기화
            self.new_collection_name = ""
            
            self.alert_message = "컬렉션이 성공적으로 생성되었습니다."
            self.show_alert = True

            success = True
            
        except Exception as e:
            self.alert_message = f"컬렉션 생성 실패: {str(e)}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield

        if success:
            yield CollectionState.load_collections
            
    async def delete_collection(self, collection_id: str):
        """지정된 ID의 컬렉션을 삭제합니다."""
        self.is_loading = True
        yield

        success = False
        try:
            client = await self._get_authenticated_client()
            response = client.from_("collections").delete().eq("id", collection_id).execute()
            self.alert_message = "컬렉션이 삭제되었습니다."
            self.show_alert = True

            success = True           
        except Exception as e:
            self.alert_message = f"컬렉션 삭제 실패: {str(e)}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield
        
        if success:
            yield CollectionState.load_collections