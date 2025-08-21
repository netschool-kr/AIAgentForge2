# AIAgentForge/state/admin_state.py 
import reflex as rx
from .base import BaseState
from .auth_state import AuthState

class AdminState(BaseState):
    """관리자 패널의 상태와 로직을 관리합니다."""
    all_users: list[dict] = []
    
    # --- [게시판 관리 기능 추가] ---
    boards: list[dict] = []
    is_loading_boards: bool = False

    async def load_all_users(self):
        # 기존 사용자 로드 로직
        pass

    async def load_all_boards(self):
        """관리자가 모든 게시판 목록을 불러옵니다."""
        self.is_loading_boards = True
        yield
        try:
            response = self.supabase_client.from_("boards").select("*").order("created_at", desc=True).execute()
            self.boards = response.data
        except Exception as e:
            print(f"Error loading boards: {e}") # 실제 프로덕션에서는 로깅 사용
        finally:
            self.is_loading_boards = False
            yield

    async def create_board(self, form_data: dict):
        """새로운 게시판을 생성합니다."""
        try:
            # 간단한 유효성 검사
            if not form_data.get("name"):
                # 실제 앱에서는 사용자에게 알림을 표시해야 함
                print("Board name is required.")
                return

            await self.get_state(AuthState).check_admin() # 관리자 권한 확인

            self.supabase_client.from_("boards").insert({
                "name": form_data["name"],
                "description": form_data.get("description", ""),
                "read_permission": form_data.get("read_permission", "user"),
                "write_permission": form_data.get("write_permission", "user"),
            }).execute()
            
            # 목록 새로고침
            yield AdminState.load_all_boards
        except Exception as e:
            print(f"Error creating board: {e}")

    async def update_board_permissions(self, board_id: str, permissions: dict):
        """게시판의 권한을 수정합니다."""
        try:
            await self.get_state(AuthState).check_admin()
            self.supabase_client.from_("boards").update(permissions).eq("id", board_id).execute()
            yield AdminState.load_all_boards
        except Exception as e:
            print(f"Error updating board: {e}")

    async def delete_board(self, board_id: str):
        """게시판을 삭제합니다."""
        try:
            await self.get_state(AuthState).check_admin()
            self.supabase_client.from_("boards").delete().eq("id", board_id).execute()
            yield AdminState.load_all_boards
        except Exception as e:
            print(f"Error deleting board: {e}")

