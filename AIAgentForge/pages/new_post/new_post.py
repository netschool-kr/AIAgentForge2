# AIAgentForge/pages/new_post.py

import reflex as rx
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.auth_state import AuthState
from AIAgentForge.state.post_state import PostState

def new_post_form() -> rx.Component:
    """새 게시글 작성을 위한 폼 컴포넌트."""
    return rx.form(
        rx.vstack(
            rx.input(
                placeholder="제목을 입력하세요",
                on_change=PostState.set_title,
                required=True,
                width="100%",
            ),
            rx.text_area(
                placeholder="내용을 입력하세요",
                on_change=PostState.set_content,
                required=True,
                width="100%",
                height="25em",
            ),
            rx.hstack(
                rx.button(
                    "취소",
                    on_click=rx.redirect("/boards/" + PostState.board_id),
                    color_scheme="gray",
                    variant="soft",
                ),
                rx.button("글 등록", type="submit"),
                spacing="4",
                justify="end",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        on_submit=PostState.create_post,#handle_post_submit,
        width="100%",
    )

@rx.page(route="/new-post/[board_id]", on_load=[AuthState.check_auth, PostState.load_board_details])
def new_post_page() -> rx.Component:
    """새 게시글을 작성하는 페이지."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.vstack(
                    rx.heading("새 글 작성", size="8"),
                    rx.text(
                        "현재 게시판: ",
                        rx.code(PostState.board_name),
                        color_scheme="gray"
                    ),
                    align="start",
                    width="100%",
                    margin_bottom="1.5em",
                ),
                new_post_form(),
                spacing="5",
            ),
            padding_y="2em",
            max_width="960px",
        ),
    )