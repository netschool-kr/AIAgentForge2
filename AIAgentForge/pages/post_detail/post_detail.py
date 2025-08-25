# AIAgentForge/pages/posts/post_detail.py

import reflex as rx
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.post_state import PostDetailState
from AIAgentForge.state.auth_state import AuthState

def post_view() -> rx.Component:
    """게시물 내용을 보여주는 컴포넌트."""
    return rx.vstack(
        rx.heading(PostDetailState.post.get("title", "제목 없음"), size="8"),
        rx.hstack(
            # rx.text(f"작성자: {PostDetailState.post.get('author_email', '알 수 없음')}", color_scheme="gray"),
            rx.spacer(),
            rx.text(f"작성일: {PostDetailState.formatted_created_at}", color_scheme="gray"),
            width="100%",
            padding_y="1em",
        ),
        rx.divider(),
        rx.box(
            PostDetailState.post.get("content", ""),
            padding_y="2em",
            width="100%",
            min_height="30vh",
        ),
        align="start",
        width="100%",
    )

def edit_post_view() -> rx.Component:
    """게시물 수정을 위한 폼 컴포넌트."""
    return rx.form(
        rx.vstack(
            rx.input(
                default_value=PostDetailState.post.get("title", ""), 
                name="title",
                width="100%",
            ),
            rx.text_area(
                default_value=PostDetailState.post.get("content", ""), 
                name="content",
                width="100%",
                height="25em",
            ),
            rx.hstack(
                rx.button("취소", on_click=PostDetailState.toggle_edit, color_scheme="gray", variant="soft"),
                rx.button("저장", type="submit"),
                justify="end",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        on_submit=PostDetailState.update_post,
    )

@rx.page(route="/posts/[post_id]", on_load=[AuthState.check_auth, PostDetailState.load_post])
def post_detail_page() -> rx.Component:
    """게시물 상세 정보를 보여주는 페이지."""
    return rx.box(
        navbar(),
        rx.container(
            rx.cond(
                PostDetailState.is_loading,
                rx.center(rx.spinner(), height="80vh"),
                rx.vstack(
                    rx.cond(
                        PostDetailState.is_editing,
                        edit_post_view(),
                        post_view(),
                    ),
                    rx.hstack(
                        rx.link(
                            rx.button("목록으로", variant="soft"),
                            href=f"/boards/{PostDetailState.post.get('board_id', '')}",
                        ),
                        rx.spacer(),
                        rx.cond(
                            PostDetailState.is_author,
                            rx.hstack(
                                rx.button("수정", on_click=PostDetailState.toggle_edit),
                                rx.alert_dialog.root(
                                    rx.alert_dialog.trigger(
                                        rx.button("삭제", color_scheme="red")
                                    ),
                                    rx.alert_dialog.content(
                                        rx.alert_dialog.title("게시물 삭제"),
                                        rx.alert_dialog.description(
                                            "정말로 이 게시물을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
                                        ),
                                        rx.flex(
                                            rx.alert_dialog.cancel(
                                                rx.button("취소", variant="soft", color_scheme="gray")
                                            ),
                                            rx.alert_dialog.action(
                                                rx.button("삭제", color_scheme="red", on_click=PostDetailState.delete_post)
                                            ),
                                            spacing="3",
                                            margin_top="16px",
                                            justify="end",
                                        ),
                                    ),
                                ),
                                spacing="3",
                            ),
                        ),
                        width="100%",
                    ),
                    spacing="5",
                    padding_y="2em",
                ),
            ),
            max_width="960px",
        ),
    )
