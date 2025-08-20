# AIAgentForge/pages/lresearch.py

import reflex as rx
from AIAgentForge.state.lresearch_state import LResearchState

def lresearch_page() -> rx.Component:
    """
    Local Deep Researcher 페이지의 UI를 구성합니다.
    """
    return rx.container(
        rx.vstack(
            # 페이지 헤더
            rx.heading("🤖 Local Deep Researcher", size="8", margin_bottom="1rem", text_align="center"),
            rx.text(
                "연구하고 싶은 주제를 입력하면, 로컬 AI 에이전트가 웹을 검색하여 심층 보고서를 작성해줍니다.",
                color_scheme="gray",
                text_align="center"
            ),
            rx.divider(margin_y="1.5rem"),

            # 입력 폼
            rx.hstack(
                rx.input(
                    placeholder="예: 양자 컴퓨팅의 현재 발전 수준은?",
                    value=LResearchState.query,
                    on_change=LResearchState.set_query,
                    size="3",
                    flex_grow=1,
                    is_disabled=LResearchState.is_running,
                ),
                rx.button(
                    "리서치 시작",
                    on_click=LResearchState.start_research,
                    size="3",
                    is_loading=LResearchState.is_running,
                    loading_text="분석 중...",
                ),
                width="100%",
                spacing="4",
            ),
            
            # 결과 표시 영역
            rx.cond(
                LResearchState.is_running | (LResearchState.report != ""),
                rx.box(
                    rx.vstack(
                        # 상태 메시지
                        rx.text(LResearchState.status_message, color_scheme="gray", margin_top="2rem"),
                        
                        # 로딩 스피너
                        rx.cond(
                            LResearchState.is_running,
                            rx.center(rx.spinner(size="3"), width="100%", height="10rem")
                        ),
                        
                        # 최종 보고서
                        rx.cond(
                            LResearchState.report,
                            rx.card(
                                rx.markdown(
                                    LResearchState.report,
                                    component_map={
                                        "h1": lambda text: rx.heading(text, size="6", margin_y="0.5rem"),
                                        "h2": lambda text: rx.heading(text, size="5", margin_y="0.5rem"),
                                        "p": lambda text: rx.text(text, as_="p", margin_bottom="0.5rem"),
                                    }
                                ),
                                width="100%",
                            )
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    margin_top="2rem",
                    width="100%",
                )
            ),
            
            width="100%",
            spacing="4",
            align="center",
        ),
        max_width="960px",
        padding="2rem",
    )
