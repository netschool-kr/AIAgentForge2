# AIAgentForge/pages/post.py
import reflex as rx
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.post_state import PostDetailState
from AIAgentForge.state.auth_state import AuthState

@rx.page(route="/posts/[post_id]", on_load=PostDetailState.load_post, title="게시글")
def post_page() -> rx.Component:
    """게시글 상세 보기 페이지 UI"""
    return rx.box(
        navbar(),
        rx.container(
            rx.cond(
                PostDetailState.is_loading,
                # 로딩 중일 때 스피너 표시
                rx.center(rx.spinner(), height="50vh"),
                # 로딩 완료 후 콘텐츠 표시
                rx.vstack(
                    # --- 게시글 헤더 ---
                    rx.vstack(
                        rx.heading(PostDetailState.post.get("title", "제목 없음"), size="8"),
                        rx.hstack(
                            rx.text(f"작성자: {PostDetailState.post.get('author_email', '알 수 없음')}", size="3", color_scheme="gray"),
                            rx.spacer(),
                            rx.text(f"작성일: {PostDetailState.formatted_created_at}", size="3", color_scheme="gray"),
                            width="100%",
                            padding_y="0.5em"
                        ),
                        align="start",
                        width="100%",
                        border_bottom="1px solid #EAEAEA",
                        padding_bottom="1em",
                        margin_bottom="2em"
                    ),

                    # --- 게시글 본문 ---
                    rx.box(
                        # Markdown 형식으로 내용을 렌더링
                        rx.markdown(PostDetailState.post.get("content", "내용 없음")),
                        min_height="30vh",
                        width="100%",
                        padding_y="1em"
                    ),
                    
                    # --- 버튼 영역 ---
                    rx.hstack(
                        # 목록으로 돌아가기 버튼
                        rx.link(
                            rx.button("목록으로", variant="soft"),
                            href=f"/boards/{PostDetailState.post.get('board_id', '')}"
                        ),
                        rx.spacer(),
                        # 작성자 본인일 경우에만 수정/삭제 버튼 표시
                        rx.cond(
                            PostDetailState.is_author,
                            rx.hstack(
                                rx.link(
                                    # TODO: 수정 페이지 경로 연결
                                    rx.button("수정", color_scheme="blue"),
                                    href="#" 
                                ),
                                rx.button(
                                    "삭제",
                                    on_click=PostDetailState.delete_post,
                                    color_scheme="red"
                                ),
                                spacing="3"
                            )
                        ),
                        width="100%",
                        margin_top="2em"
                    ),
                    spacing="5",
                    width="100%",
                    padding_top="2em"
                )
            ),
            padding_x="1em",
            max_width="960px",
        )
    )
