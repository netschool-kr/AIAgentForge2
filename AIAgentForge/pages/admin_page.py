# AIAgentForge/pages/admin_page.py
import reflex as rx
from AIAgentForge.state.admin_state import AdminState
from .email import email_page # email_page를 가져옵니다.
from AIAgentForge.components.navbar import navbar # Navbar 임포트

def admin_page() -> rx.Component:
    """관리자 전용 대시보드 UI."""
    # 최상위 컴포넌트를 rx.container에서 rx.box로 변경하여 전체 너비를 사용합니다.
    return rx.box(
        navbar(), # navbar를 페이지 최상단에 추가합니다.
        rx.box( # 콘텐츠 영역에 별도의 box를 두어 패딩을 관리합니다.
            rx.heading("관리자 대시보드", size="8", margin_bottom="1em"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("메인", value="main"),
                    rx.tabs.trigger("이메일 전송", value="email"),
                    width="100%", 
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.text("이 페이지는 관리자만 접근할 수 있습니다."),
                        # 여기에 기존 관리자 페이지 콘텐츠 (사용자 목록 테이블, 시스템 통계 등)를 추가합니다.
                        width="100%",
                        padding_x="4em",
                        padding_y="4em",
                    ),
                    value="main",
                    width="100%", 
                ),
                rx.tabs.content(
                    email_page(), # email_page 컴포넌트를 렌더링합니다.
                    value="email",
                    width="100%", 
                ),
                defaultValue="main",
                width="100%", # 탭 컴포넌트가 전체 너비를 차지하도록 설정
            ),
            padding_x="2em", # 콘텐츠 좌우에 여백을 줍니다.
            padding_y="2em", # 콘텐츠 상하에 여백을 줍니다.
        ),
        width="100%", # 전체 너비 사용
    )
