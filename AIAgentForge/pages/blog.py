# blog_page.py
import reflex as rx
from ..state.blog_state import BlogState
from AIAgentForge.components.navbar import navbar

def step_card(*children, **props):
    """단계별 UI를 감싸는 카드 컴포넌트입니다."""
    return rx.card(
        rx.vstack(
            *children,
            spacing="4",
            align="stretch",
        ),
        width="100%",
        **props
    )

def blog_page() -> rx.Component:
    """블로그 포스팅 생성기 메인 페이지 UI입니다."""
    return rx.container(
        rx.vstack(
            navbar(),
            rx.heading("AI 블로그 포스팅 생성기 🤖", size="8", text_align="center"),
            rx.text("제품 키워드를 입력하면 AI가 제목, 목차, 본문까지 자동으로 생성해줍니다.", text_align="center"),
            
            rx.divider(margin_y="6"),

            # --- 1단계: 키워드 입력 ---
            step_card(
                rx.heading("Step 1: 제품 키워드 입력", size="5"),
                rx.hstack(
                    rx.input(
                        placeholder="예: LG 트롬 오브제컬렉션 워시타워",
                        value=BlogState.product_keyword,
                        on_change=BlogState.set_product_keyword,
                        on_blur=BlogState.generate_titles,
                        on_key_down=BlogState.handle_key_down,
                        size="3",
                        flex_grow=1,
                    ),
                    rx.button(
                        "제목 생성하기",
                        on_click=BlogState.generate_titles,
                        is_loading=BlogState.is_generating_titles,
                        size="3",
                    ),
                    width="100%",
                ),
            ),

            # --- 2단계: 제목 선택 ---
            rx.cond(
                BlogState.is_generating_titles | (BlogState.title_candidates.length() > 0),
                step_card(
                    rx.heading("Step 2: 마음에 드는 제목 선택", size="5"),
                    rx.cond(
                        BlogState.is_generating_titles,
                        rx.center(rx.spinner()),
                        rx.vstack(
                            rx.foreach(
                                BlogState.title_candidates,
                                lambda title: rx.button(
                                    title,
                                    on_click=lambda: BlogState.select_title_and_generate_outline(title),
                                    width="100%",
                                    variant="outline",
                                    is_disabled=BlogState.is_generating_outline,
                                )
                            ),
                            spacing="3",
                            width="100%",
                        ),
                    ),
                ),
            ),

            # --- 3단계: 목차 확인 및 본문 생성 ---
            rx.cond(
                BlogState.is_generating_outline | (BlogState.generated_outline != ""),
                step_card(
                    rx.heading("Step 3: 생성된 목차 확인", size="5"),
                    rx.cond(
                        BlogState.is_generating_outline,
                        rx.center(rx.spinner()),
                        rx.box(
                            rx.text(BlogState.generated_outline, white_space="pre-wrap"),
                            background_color=rx.color("gray", 3),
                            padding="4",
                            border_radius="var(--radius-3)",
                            width="100%",
                        ),
                    ),
                    rx.button(
                        "최종 포스팅 생성하기",
                        on_click=BlogState.generate_final_posting,
                        is_loading=BlogState.is_generating_posting,
                        size="3",
                        width="100%",
                        disabled=BlogState.generated_outline == "",
                    ),
                ),
            ),
            
            # --- 4단계: 최종 결과물 ---
            rx.cond(
                BlogState.is_generating_posting | BlogState.is_finished,
                step_card(
                    rx.heading("Step 4: 완성된 포스팅", size="5"),
                    rx.cond(
                        BlogState.is_generating_posting,
                        rx.center(rx.spinner()),
                        rx.box(
                            rx.markdown(BlogState.final_posting),
                            border="1px solid",
                            border_color=rx.color("gray", 6),
                            padding="6",
                            border_radius="var(--radius-3)",
                            width="100%",
                        ),
                    ),
                ),
            ),

            # --- 새로 시작하기 버튼 ---
            rx.cond(
                BlogState.is_finished,
                rx.center(
                    rx.button("새로 시작하기", on_click=BlogState.reset_all, size="3", margin_top="6"),
                    width="100%",
                )
            ),

            spacing="6",
            width="100%",
            margin_x="auto",
            padding_y="8",
        ),
        size="4",  # 컨테이너 크기를 최대로 설정하여 좌우 여백을 줄입니다.
        on_mount=BlogState.init_state,
    )
