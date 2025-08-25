# AIAgentForge/pages/boards/board_detail.py

import reflex as rx
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.post_state import PostState
from AIAgentForge.state.auth_state import AuthState


def post_list() -> rx.Component:
    """
    DB에 저장된 게시물 목록을 표시하는 컴포넌트입니다.
    각 행을 클릭하면 해당 게시물의 상세 페이지로 이동합니다.
    """
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("제목"),
                rx.table.column_header_cell("생성일"),
            )
        ),
        rx.table.body(
            rx.foreach(
                PostState.posts,
                lambda post: rx.table.row(
                    rx.table.cell(post["title"]),
                    rx.table.cell(post["created_at"]),
                    # on_click 이벤트를 State의 이벤트 핸들러로 변경
                    on_click=PostState.go_to_post(post["id"]),
                    _hover={
                        "cursor": "pointer", 
                        "background_color": rx.color("gray", 3)
                    },
                )
            )
        ),
        width="100%",
    )
    
@rx.page(route="/boards/[board_id]", on_load=[AuthState.check_auth, PostState.load_board_and_posts])
def board_detail_page() -> rx.Component:
    """특정 게시판의 게시글 목록을 보여주는 페이지."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.vstack(
                    rx.heading(PostState.board_name, size="8"),
                    rx.text(PostState.board_description, color_scheme="gray"),
                    align="start",
                    width="100%",
                    margin_bottom="1.5em",
                ),
                
                rx.hstack(
                    rx.form(
                        rx.hstack(
                            rx.input(
                                value=rx.cond(PostState.search_query, PostState.search_query, ""),
                                on_change=PostState.set_search_query,
                                placeholder="제목 또는 내용으로 검색...",
                            ),
                            rx.button("검색", type="submit"),
                        ),
                        on_submit=PostState.handle_search,
                    ),
                    rx.spacer(),
                    rx.link(
                        rx.button("글쓰기", white_space="nowrap"),
                        # PostState.board_id가 아닌 PostState.curr_board_id를 사용해야 합니다.
                        href="/new-post/" + PostState.curr_board_id
                    ),
                    width="100%",
                    margin_bottom="1.5em",
                ),

                rx.cond(
                    PostState.is_loading,
                    rx.center(rx.spinner(), height="30vh"),
                    post_list()
                ),
                spacing="5",
            ),
            padding_y="2em",
            max_width="960px",
        ),
    )
