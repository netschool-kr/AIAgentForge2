# AIAgentForge/pages/dashboard.py:
import reflex as rx
from AIAgentForge.state.dashboard_state import DashboardState
from AIAgentForge.state.board_state import BoardState
from AIAgentForge.state.auth_state import AuthState  # AuthState 임포트 추가
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
        on_click=lambda: rx.console_log(f"Navigating to board {board['id']}"),# Debug
        width="100%",
    )

# --- [수정된 부분] ---
# @rx.page 데코레이터를 추가하여 페이지 로드 이벤트를 설정합니다.
# 사용자가 로그인했는지 먼저 확인하고, 게시판 목록을 불러옵니다.
@rx.page(route="/dash_boards", on_load=[AuthState.check_auth, BoardState.load_visible_boards])
def dashboard_page() -> rx.Component:
    """
    대시보드의 메인 페이지 UI를 정의하는 컴포넌트 함수입니다.
    """
    return rx.vstack(
        navbar(),
        rx.heading("사용자 대시보드", size="8"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("이름"),
                    rx.table.column_header_cell("나이"),
                    rx.table.column_header_cell("역할"),
                )
            ),
            # 테이블 본문을 추가하고 상태와 연결합니다.
            rx.table.body(
                rx.foreach(
                    DashboardState.users,
                    lambda user: rx.table.row(
                        rx.table.cell(user["name"]),
                        rx.table.cell(user["age"]),
                        rx.table.cell(user["role"]),
                    ),
                )
            ),
        ),
        rx.divider(),

        # Recharts를 사용한 막대 차트 추가
        rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="age", stroke="#8884d8", fill="#8884d8"
            ),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(),
            data=DashboardState.users, # 테이블과 동일한 상태를 사용
            height=300,
            width="100%",
        ),
        
        rx.divider(),
        # 폼 컴포넌트로 상호작용 부분을 감싸고 이벤트 핸들러를 연결합니다.
        rx.form(
            rx.hstack(
                rx.input(placeholder="이름", name="name", required=True),
                rx.input(placeholder="나이", name="age", type="number", required=True),
                rx.button("사용자 추가", type="submit"),
                justify="center",
            ),
            on_submit=DashboardState.add_user,
            reset_on_submit=True,
            align="center",
        ),
                
        rx.divider(),
        rx.heading("게시판 목록", size="8", margin_bottom="1em"),
        rx.cond(
            BoardState.is_loading_boards,
            rx.center(rx.spinner(), height="20vh"), # 로딩 중일 때 스피너 표시
            rx.vstack(
                # visible_boards 리스트를 순회하며 board_card를 렌더링
                rx.foreach(
                    BoardState.visible_boards,
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

@rx.page(route="/boards", on_load=[AuthState.check_auth, BoardState.load_visible_boards])
def board_page() -> rx.Component:
    """
    대시보드의 메인 페이지 UI를 정의하는 컴포넌트 함수입니다.
    """
    return rx.vstack(
        navbar(),
                
        rx.divider(),
        rx.heading("게시판 목록", size="8", margin_bottom="1em"),
        rx.cond(
            BoardState.is_loading_boards,
            rx.center(rx.spinner(), height="20vh"), # 로딩 중일 때 스피너 표시
            rx.vstack(
                # visible_boards 리스트를 순회하며 board_card를 렌더링
                rx.foreach(
                    BoardState.visible_boards,
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
