import reflex as rx
from ..state.research_state import ResearchState
from AIAgentForge.components.navbar import navbar

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

def sub_question_editor() -> rx.Component:
    """A component to edit the list of sub-questions."""
    return rx.vstack(
        # Use rx.foreach to create an input for each sub-question.
        # The lambda function receives the item and its index 'i'.
        rx.foreach(
            ResearchState.sub_questions,
            lambda item, i: rx.hstack(
                rx.input(
                    value=item,
                    on_change=lambda val: ResearchState.update_sub_question(i, val),
                    placeholder=f"하위 질문 #{i + 1}",
                    width="100%",
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=20),
                    on_click=lambda: ResearchState.delete_sub_question(i),
                    variant="soft",
                    color_scheme="red",
                ),
                width="100%",
                spacing="2",
            )
        ),
        # Buttons to add a new question and to start the research
        rx.hstack(
            rx.button(
                "질문 추가",
                on_click=ResearchState.add_sub_question,
                variant="outline",
                margin_top="10px",
            ),
            rx.spacer(),
            rx.button(
                "수정된 질문으로 리서치 시작",
                on_click=ResearchState.run_research_on_sub_questions,
                is_disabled=ResearchState.is_generating,
                size="3",
                margin_top="10px",
            ),
            justify="between",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )

def research_page() -> rx.Component:
    """The main UI of the application."""
    return rx.container(
        rx.vstack(
            navbar(),
            rx.heading("Reflex를 이용한 AI 자동 리서치 에이전트", size="8", margin_bottom="10px", text_align="center"),
            rx.text("연구 질문을 입력하면 AI 에이전트가 여러 단계에 걸쳐 심층 보고서를 생성합니다.", text_align="center"),

            # Input Form (Visible only at the start)
            rx.cond(
                ResearchState.research_stage == "initial",
                rx.form(
                    rx.vstack(
                        rx.text_area(
                            name="main_question",
                            placeholder="예: 양자 컴퓨팅의 현재 발전 수준과 미래 전망은?",
                            width="100%",
                            height="120px",
                            is_required=True,
                        ),
                        rx.button(
                            "하위 질문 생성",
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
                    on_submit=ResearchState.generate_sub_questions_for_editing,
                    width="100%",
                ),
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
                # Sub-questions Editor (Visible during editing stage)
                rx.cond(
                    ResearchState.research_stage == "editing_subquestions",
                    result_card(
                        "생성된 하위 질문 (편집 가능)",
                        sub_question_editor()
                    )
                ),
                
                # --- [FIXED] Changed .is_in to use logical OR operator ---
                # Static list of sub-questions (Visible after editing is done)
                rx.cond(
                    (ResearchState.research_stage == "researching") | (ResearchState.research_stage == "complete"),
                    result_card(
                        "리서치에 사용된 하위 질문",
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
