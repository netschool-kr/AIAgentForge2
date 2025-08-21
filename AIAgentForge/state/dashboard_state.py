#AIAgentForge/AIAgentForge/state/dashboard_state.py:
import reflex as rx
from.base import BaseState
from .auth_state import AuthState

class DashboardState(BaseState):
    """
    대시보드 페이지의 상태를 관리하는 클래스입니다.
    대시보드와 관련된 모든 변수(vars)와 이벤트 핸들러(event handlers)는
    이 클래스 내에 정의됩니다.
    """
    
    # 사용자 목록을 저장할 기본 변수(Base Var).
    # 초기 데이터로 두 명의 사용자를 하드코딩합니다.
    users: list[dict] = [
        {"name": "존 도", "age": 30, "role": "개발자"},
        {"name": "제인 도", "age": 28, "role": "디자이너"},
    ]
    # --- [접근 가능한 게시판 목록 기능 추가] ---
    visible_boards: list[dict] = []
    is_loading_boards: bool = False

    async def load_visible_boards(self):
        """사용자가 접근 권한을 가진 게시판 목록만 불러옵니다."""
        self.is_loading_boards = True
        yield
        try:
            auth_state = await self.get_state(AuthState)
            
            # RLS 정책이 자동으로 필터링해주므로, 그냥 select만 호출하면 됩니다.
            # Supabase는 이 요청을 보낸 사용자의 권한에 맞는 데이터만 반환합니다.
            response = self.supabase_client.from_("boards").select("*").order("name").execute()
            self.visible_boards = response.data
        except Exception as e:
            print(f"Error loading visible boards: {e}")
        finally:
            self.is_loading_boards = False
            yield

    def add_user(self, form_data: dict):
            """폼 데이터로부터 새로운 사용자를 추가하는 이벤트 핸들러."""
            # 간단한 유효성 검사
            if not form_data.get("name") or not form_data.get("age"):
                return rx.window_alert("이름과 나이는 비워둘 수 없습니다!")

            # 상태 업데이트
            self.users.append(
                {
                    "name": form_data["name"],
                    "age": int(form_data["age"]),
                    "role": "신규 사용자",
                }
            )

    @rx.var
    def total_users(self) -> int:
        """사용자 리스트의 길이를 반환하는 계산 변수."""
        return len(self.users)
            