    # AIAgentForge/pages/board_page.py (신규 파일 생성)
import reflex as rx
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.post_state import PostState
from AIAgentForge.state.auth_state import AuthState

def post_list_item(post: dict) -> rx.Component:
    """게시글 목록의 각 항목을 렌더링하는 컴포넌트."""
    return rx.link(
        rx.hstack(
            rx.text(post["title"], width="60%"),
            rx.spacer(),
            rx.text(post.get("author_email", "익명"), width="25%"),
            rx.text(
                post["created_at"].replace("T", " ")[:10], # 날짜 부분만 표시
                width="15%",
                text_align="right",
            ),
            width="100%",
            padding="0.8em",
            border_bottom="1px solid #EAEAEA",
            _hover={"background_color": rx.color("gray", 2)},
        ),
        href=f"/posts/{post['id']}", # 클릭 시 게시글 상세 페이지로 이동
    )

@rx.page(route="/boards", on_load=[AuthState.check_auth, PostState.load_board_and_posts])
def board_page() -> rx.Component:
    """특정 게시판의 게시글 목록을 보여주는 페이지."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # --- 게시판 헤더 ---
                rx.vstack(
                    rx.heading(PostState.board_name, size="8"),
                    rx.text(PostState.board_description, color_scheme="gray"),
                    align="start",
                    width="100%",
                    margin_bottom="1.5em",
                ),
                
                # --- 검색 및 글쓰기 버튼 ---
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
                    # TODO: 새 글 작성 페이지로 연결
                    rx.link(
                        rx.button("글쓰기"),
                        href=f"/new-post/{PostState.current_board_id}" # 예: f"/new-post/{PostState.current_board_id}"
                    ),
                    width="100%",
                    margin_bottom="1.5em",
                ),

                # --- 게시글 목록 ---
                rx.cond(
                    PostState.is_loading,
                    rx.center(rx.spinner(), height="30vh"),
                    rx.vstack(
                        rx.foreach(
                            PostState.posts,
                            post_list_item,
                        ),
                        width="100%",
                    ),
                ),
                spacing="5",
            ),
            padding_y="2em",
            max_width="960px",
        ),
        # 페이지 로드 시 PostState.load_board_and_posts 이벤트가 자동으로 호출됩니다.
        # (AIAgentForge.py 파일에 on_load 설정이 필요합니다.)
        on_load=PostState.load_board_and_posts,
    )
