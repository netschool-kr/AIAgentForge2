# AIAgentForge/pages/dashboard.py:
import reflex as rx
from AIAgentForge.state.dashboard_state import DashboardState
from AIAgentForge.components.navbar import navbar

def board_card(board: dict) -> rx.Component:
    """개별 게시판을 표시하는 카드 컴포넌트."""
    return rx.link(
        rx.card(
            rx.vstack(
                rx.heading(board["name"], size="5"),
                rx.text(
                    board.get("description", "설명이 없습니다."),
                    size="2",
                    color_scheme="gray",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            as_child=True, # Card 전체를 클릭 가능하게 만듭니다.
            width="100%",
            _hover={"background_color": rx.color("gray", 2)},
        ),
        href=f"/boards/{board['id']}", # 클릭 시 해당 게시판의 글 목록 페이지로 이동
        width="100%",
    )

def dashboard_page() -> rx.Component:
    """
    대시보드의 메인 페이지 UI를 정의하는 컴포넌트 함수입니다.
    """
    return rx.vstack(
        navbar(),
        rx.heading("게시판 목록", size="8", margin_bottom="1em"),
        rx.cond(
            DashboardState.is_loading_boards,
            rx.center(rx.spinner(), height="20vh"), # 로딩 중일 때 스피너 표시
            rx.vstack(
                # visible_boards 리스트를 순회하며 board_card를 렌더링
                rx.foreach(
                    DashboardState.visible_boards,
                    board_card,
                ),
                spacing="4",
                width="100%",
                max_width="800px",
            ),
        ),
        spacing="5",
        align="center",
        padding_y="2em",
        width="100%",
    )
