# AIAgentForge/pages/admin_page.py
import reflex as rx
from AIAgentForge.state.admin_state import AdminState
from .email import email_page 
from AIAgentForge.components.navbar import navbar

def board_management_content() -> rx.Component:
    """게시판 관리 탭의 콘텐츠를 렌더링하는 컴포넌트."""
    return rx.vstack(
        # --- 1. 새 게시판 생성 폼 ---
        rx.card(
            rx.form(
                rx.vstack(
                    rx.heading("새 게시판 생성", size="5"),
                    rx.input(name="name", placeholder="게시판 이름", required=True),
                    rx.input(name="description", placeholder="게시판 설명"),
                    rx.hstack(
                        rx.text("읽기 권한:"),
                        rx.select(
                            ["guest", "user", "admin"],
                            name="read_permission",
                            default_value="user",
                        ),
                        rx.text("쓰기 권한:"),
                        rx.select(
                            ["user", "admin"],
                            name="write_permission",
                            default_value="user",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    rx.button("생성하기", type="submit"),
                    spacing="4",
                ),
                on_submit=AdminState.create_board,
                reset_on_submit=True,
            ),
            width="100%",
        ),
        
        rx.divider(margin_y="2em"),

        # --- 2. 게시판 목록 및 관리 ---
        rx.heading("게시판 목록", size="5", margin_bottom="1em"),
        rx.cond(
            AdminState.is_loading_boards,
            rx.center(rx.spinner()),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("이름"),
                        rx.table.column_header_cell("설명"),
                        rx.table.column_header_cell("읽기 권한"),
                        rx.table.column_header_cell("쓰기 권한"),
                        rx.table.column_header_cell("관리"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        AdminState.boards,
                        lambda board: rx.table.row(
                            rx.table.cell(board["name"]),
                            rx.table.cell(board["description"]),
                            rx.table.cell(board["read_permission"]),
                            rx.table.cell(board["write_permission"]),
                            rx.table.cell(
                                rx.button(
                                    "삭제",
                                    on_click=lambda: AdminState.delete_board(board["id"]),
                                    color_scheme="red",
                                    size="1",
                                )
                            ),
                        )
                    )
                ),
                variant="surface",
                width="100%",
            ),
        ),
        spacing="5",
        width="100%",
        padding_x="2em",
        padding_y="2em",
    )

@rx.page(route="/admin", on_load=AdminState.load_all_boards)
def admin_page() -> rx.Component:
    """관리자 전용 대시보드 UI."""
    return rx.box(
        navbar(),
        rx.box(
            rx.heading("관리자 대시보드", size="8", margin_bottom="1em"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("메인", value="main"),
                    rx.tabs.trigger("게시판 관리", value="board_management"), # 새 탭 추가
                    rx.tabs.trigger("이메일 전송", value="email"),
                    width="100%", 
                ),
                # --- 메인 탭 ---
                rx.tabs.content(
                    rx.vstack(
                        rx.text("이 페이지는 관리자만 접근할 수 있습니다."),
                        width="100%",
                        padding_x="4em",
                        padding_y="4em",
                    ),
                    value="main",
                    width="100%", 
                ),
                # --- 게시판 관리 탭 ---
                rx.tabs.content(
                    board_management_content(), # 게시판 관리 컴포넌트 렌더링
                    value="board_management",
                    width="100%",
                ),
                # --- 이메일 전송 탭 ---
                rx.tabs.content(
                    email_page(),
                    value="email",
                    width="100%", 
                ),
                defaultValue="main",
                width="100%",
            ),
            padding_x="2em",
            padding_y="2em",
        ),
        width="100%",
    )
