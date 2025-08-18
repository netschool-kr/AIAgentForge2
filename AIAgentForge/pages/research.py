import reflex as rx
from ..state.research_state import ResearchState
from AIAgentForge.components.navbar import navbar  # Navbar 임포트 추가

def result_card(title: str, content: rx.Component) -> rx.Component:
    """A styled card component to display a section of the results."""
    return rx.card(
        rx.vstack(
            rx.heading(title, size="5", margin_bottom="10px"),
            rx.divider(),
            content,
            spacing="4",
            width="100%",
        ),
        width="100%",
    )

def research_page() -> rx.Component:
    """The main UI of the application."""
    return rx.container(
        rx.vstack(
            navbar(),
            rx.heading("Reflex를 이용한 AI 자동 리서치 에이전트", size="8", margin_bottom="10px", text_align="center"),
            rx.text("연구 질문을 입력하면 AI 에이전트가 여러 단계에 걸쳐 심층 보고서를 생성합니다.", text_align="center"),

            # Input Form
            rx.form(
                rx.vstack(

                    # rx.input(
                    #     name="tavily_api_key",
                    #     placeholder="Tavily API 키를 입력하세요 (tavily.com)",
                    #     type="password",
                    #     width="100%",
                    #     is_required=True,
                    # ),
                    rx.text_area(
                        name="main_question",
                        placeholder="예: 양자 컴퓨팅의 현재 발전 수준과 미래 전망은?",
                        width="100%",
                        height="120px",
                        is_required=True,
                    ),
                    rx.button(
                        "리서치 시작",
                        type="submit",
                        size="3",
                        width="100%",
                        is_disabled=rx.cond(
                            ResearchState.is_generating | ~ResearchState.is_form_valid,
                            True,
                            False
                        ),
                    ),
                    spacing="4",
                ),
                on_submit=ResearchState.start_research_process,
                width="100%",
            ),

            # Loading/Status Indicator
            rx.cond(
                ResearchState.is_generating,
                rx.center(
                    rx.hstack(
                        rx.spinner(),
                        rx.text(ResearchState.current_status),
                        spacing="4",
                        align="center",
                    ),
                    width="100%",
                    margin_top="20px",
                )
            ),

            # Results Display Area
            rx.vstack(
                # Sub-questions
                rx.cond(
                    ResearchState.sub_questions,
                    result_card(
                        "생성된 하위 질문",
                        # --- [FIXED] Changed to use rx.foreach for dynamic list rendering ---
                        rx.ordered_list(
                            rx.foreach(
                                ResearchState.sub_questions,
                                lambda item: rx.list_item(item)
                            )
                        )
                    )
                ),
                # Research Summaries
                rx.cond(
                    ResearchState.research_results,
                    result_card(
                        "하위 질문별 리서치 요약",
                        # --- [FIXED] Changed to use rx.foreach for dynamic list rendering ---
                        rx.vstack(
                            rx.foreach(
                                ResearchState.research_results,
                                lambda res: rx.box(
                                    rx.heading(res["sub_question"], size="3"),
                                    rx.markdown(res["summary"]),
                                    border="1px solid #ddd",
                                    padding="15px",
                                    border_radius="8px",
                                    width="100%",
                                )
                            ),
                            spacing="4",
                            width="100%"
                        )
                    )
                ),
                # Final Report
                rx.cond(
                    ResearchState.report,
                    result_card(
                        "최종 보고서",
                        rx.markdown(
                            ResearchState.report,
                            component_map={
                                "h1": lambda text: rx.heading(text, size="7", margin_y="15px"),
                                "h2": lambda text: rx.heading(text, size="6", margin_y="12px"),
                                "h3": lambda text: rx.heading(text, size="5", margin_y="10px"),
                            }
                        )
                    )
                ),
                spacing="6",
                width="100%",
                margin_top="30px",
            ),
            spacing="6",
            width="100%",
            max_width="960px",
            padding_x="20px",
            padding_y="30px",
        ),
        center_content=True,
    )
