# AIAgentForge/state/collection_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState
from postgrest import SyncPostgrestClient
import os
from dotenv import load_dotenv
from typing import Optional
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

class CollectionState(BaseState):
    """컬렉션 관리와 관련된 모든 상태와 로직을 중앙에서 관리합니다."""

    collections: list[dict] = []
    is_loading: bool = False
    
    show_alert: bool = False
    alert_message: str = ""
    show_confirm_modal: bool = False
    
    collection_id_to_delete: Optional[str] = None

    @rx.event
    def set_show_confirm_modal(self, open: bool):
        """Sets the visibility of the confirmation modal."""
        self.show_confirm_modal = open
        if not open:
            self.collection_id_to_delete = None

    @rx.event
    def show_confirm(self, collection_id: str):
        """Show confirmation modal for deletion."""
        self.collection_id_to_delete = collection_id
        self.set_show_confirm_modal(True)

    @rx.event
    def cancel_delete(self):
        """Cancel deletion by closing the modal."""
        self.set_show_confirm_modal(False)

   
    # ID를 먼저 지역 변수에 저장한 후 삭제 작업을 수행하도록 로직을 변경합니다.
    @rx.event
    async def confirm_delete(self):
        """Confirm and perform deletion."""
        # 1. 상태가 변경되기 전에 ID를 지역 변수에 저장합니다.
        collection_id = self.collection_id_to_delete

        # 2. 다이얼로그를 닫습니다. 이 때 collection_id_to_delete는 None이 됩니다.
        self.set_show_confirm_modal(False)

        # 3. 저장해둔 지역 변수에 ID가 있는지 확인합니다.
        if collection_id is None:
            return

        try:
            # 4. 지역 변수의 ID를 사용하여 삭제를 수행합니다.
            client = await self._get_authenticated_client()
            client.from_("collections").delete().eq("id", collection_id).execute()
            # 5. 목록을 새로고침합니다.
            yield CollectionState.load_collections
        except Exception as e:
            self.alert_message = f"삭제 실패: {e}"
            self.show_alert = True
            yield

    # async def _get_authenticated_client(self):
    #     """Create authenticated Postgrest client with user's token."""
    #     auth_state = await self.get_state(AuthState)
    #     if not auth_state.is_authenticated or not hasattr(auth_state, 'access_token'):
    #         raise Exception("Not authenticated or no token available")
    #     return SyncPostgrestClient(
    #         f"{SUPABASE_URL}/rest/v1",
    #         headers={
    #             "apikey": SUPABASE_KEY,
    #             "Authorization": f"Bearer {auth_state.access_token}",
    #         }
    #     )
        
    async def load_collections(self):
        """사용자 소유의 모든 컬렉션을 데이터베이스에서 불러옵니다."""
        self.is_loading = True
        yield
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                self.is_loading = False
                return
            
            client = await self._get_authenticated_client()
            response = client.from_("collections").select("*").eq("owner_id", auth_state.user.id).order("created_at", desc=True).execute()
            self.collections = response.data
        except Exception as e:
            self.alert_message = f"컬렉션 로딩 실패: {str(e)}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield
    
    async def create_collection(self, form_data: dict):
        """새로운 컬렉션을 생성합니다."""
        collection_name = form_data.get("name")
        if not collection_name or not collection_name.strip():
            self.alert_message = "컬렉션 이름은 비워둘 수 없습니다."
            self.show_alert = True
            yield
            return

        self.is_loading = True
        yield
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                raise Exception("User not found")

            client = await self._get_authenticated_client()
            client.from_("collections").insert({
                "name": collection_name,
                "owner_id": auth_state.user.id
            }).execute()
            
            self.alert_message = "컬렉션이 성공적으로 생성되었습니다."
            self.show_alert = True
            yield CollectionState.load_collections
        except Exception as e:
            self.alert_message = f"컬렉션 생성 실패: {str(e)}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield
