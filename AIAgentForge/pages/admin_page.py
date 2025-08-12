
# AIAgentForge/pages/admin_page.py (신규 생성)
import reflex as rx
from AIAgentForge.state.admin_state import AdminState

def admin_page() -> rx.Component:
    """관리자 전용 대시보드 UI."""
    return rx.container(
        rx.heading("관리자 대시보드", size="8"),
        rx.text("이 페이지는 관리자만 접근할 수 있습니다."),
        # 여기에 사용자 목록 테이블, 시스템 통계 등을 추가합니다.
    )
