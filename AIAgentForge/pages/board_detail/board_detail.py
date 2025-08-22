# AIAgentForge/pages/boards/board_detail.py

import reflex as rx
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.post_state import PostState
from AIAgentForge.state.auth_state import AuthState


def post_list() -> rx.Component:
    """
    DB에 저장된 게시물 목록을 표시하는 컴포넌트입니다.
    """

    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("제목"),
                rx.table.column_header_cell("생성일"),
                # rx.table.column_header_cell("작업"),                
            )
        ),
        rx.table.body(
            rx.foreach(
                PostState.posts,
                lambda post: rx.table.row(
                    rx.table.cell(post["title"]),
                    rx.table.cell(post["created_at"]),
                    # rx.table.cell(
                    #     rx.button(
                    #         "삭제", 
                    #         color_scheme="red", 
                    #         variant="soft",
                    #         on_click=PostState.delete(post["id"])  # 삭제 핸들러 추가 (doc에 "id" 키가 있다고 가정)
                    #     )
                    # ),                    
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
                                value=PostState.search_query,
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
                        href="/new-post/" + PostState.board_id
                    ),
                    width="100%",
                    margin_bottom="1.5em",
                ),

                # 수정된 부분: collection_detail.py와 같이 구조를 단순화했습니다.
                rx.cond(
                    PostState.is_loading,
                    rx.center(rx.spinner(), height="30vh"),
                    post_list()  # 로딩이 끝나면 post_list 함수를 호출
                ),
                spacing="5",
            ),
            padding_y="2em",
            max_width="960px",
        ),
    )
