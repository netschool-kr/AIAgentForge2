"""
AIAgentForge/pages/search.py

이 파일은 Reflex를 사용하여 검색 페이지의 UI와 상태 관리를 구현합니다.
UI는 상태(State)의 함수라는 선언적 패러다임을 따릅니다.
"""

import reflex as rx
from typing import Dict, Any
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.search_state import SearchState
from AIAgentForge.state.document_state import DocumentState

# 검색 결과 항목을 위한 타입 정의
SearchResult = Dict[str, Any]

def render_search_result(result: SearchResult) -> rx.Component:
    """
    개별 검색 결과를 표시하는 카드 컴포넌트를 렌더링하는 함수.
    LLM 답변의 근거가 된 소스 문서를 보여주기 위해 사용됩니다.
    """
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(f"ID: {result['id']}", size="3"),
                rx.spacer(),
                rx.badge(f"Score: {result['rrf_score']:.2f}", color_scheme="green"),
                align="center",
                width="100%"
            ),
            rx.text(result['content'], as_="p", size="2", color_scheme="gray"),
            spacing="2",
            width="100%"
        ),
        width="100%",
    )

@rx.page(route="/search", title="하이브리드 검색")
def search_page() -> rx.Component:
    """
    검색 페이지의 전체 UI를 구성하고 반환합니다.
    """
    return rx.container(
        rx.vstack(
            navbar(),
            rx.heading(f"하이브리드 검색 엔진 ({DocumentState.collection_name})", size="7", align="center", margin_bottom="1em"),
            
            # 검색 입력창과 버튼을 form으로 감싸서 Enter 키 입력을 처리합니다.
            rx.form(
                rx.hstack(
                    rx.input(
                        value=SearchState.search_query,
                        on_change=SearchState.set_search_query,
                        placeholder="질문을 입력하세요...",
                        size="3",
                        flex_grow=1,
                    ),
                    rx.button(
                        "검색",
                        is_loading=SearchState.is_loading,
                        size="3",
                        type_="submit",  # 버튼 타입을 'submit'으로 설정
                    ),
                    spacing="2",
                    width="100%",
                ),
                on_submit=SearchState.handle_search,  # form 제출 시 handle_search 호출
                width="100%",
            ),

            rx.divider(margin_y="2em"),

            # 로딩 및 결과 표시를 위한 조건부 렌더링
            rx.cond(
                SearchState.is_loading,
                # 로딩 중일 때: 스피너 표시
                rx.center(rx.spinner(size="3"), width="100%"),
                # 로딩이 아닐 때: 결과 표시
                rx.vstack(
                    # LLM 답변 표시
                    rx.cond(
                        SearchState.llm_answer,
                        rx.vstack(
                            rx.heading("답변", size="5"),
                            rx.card(
                                rx.markdown(SearchState.llm_answer),
                                width="100%"
                            ),
                            align="start",
                            width="100%"
                        ),
                        # 초기 메시지 표시 (LLM 답변이 아직 없을 때)
                        rx.center(
                            rx.text("질문을 입력하면 문서 기반의 답변을 생성합니다.", color_scheme="gray"),
                            width="100%",
                            height="10em"
                        ),
                    ),
                    
                    # 근거 문서(소스) 표시
                    rx.cond(
                        SearchState.search_results,
                        rx.vstack(
                            rx.heading("참고 문서", size="5", margin_top="2em"),
                            rx.foreach(
                                SearchState.search_results,
                                render_search_result,
                            ),
                            spacing="4",
                            width="100%",
                            align="start"
                        )
                    ),
                    spacing="5",
                    width="100%"
                )
            ),
            spacing="4",
            width="100%",
            max_width="960px",
        ),
        padding_x="1em",
        padding_y="2em",
    )
