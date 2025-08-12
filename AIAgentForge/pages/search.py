"""
AIAgentForge/pages/search.py

이 파일은 Reflex를 사용하여 검색 페이지의 UI와 상태 관리를 구현합니다.
UI는 상태(State)의 함수라는 선언적 패러다임을 따릅니다.
"""

import reflex as rx
import asyncio
from typing import List, Dict, Any

# 검색 결과 항목을 위한 타입 정의
SearchResult = Dict[str, Any]

class SearchState(rx.State):
    """
    검색 페이지의 모든 상태와 이벤트 핸들러를 관리하는 클래스.
    """
    # 검색어 입력을 위한 변수
    search_query: str = ""
    
    # 검색 결과를 저장할 리스트. 각 항목은 딕셔너리 형태입니다.
    search_results: List[SearchResult] = []
    
    # 검색 진행 상태(로딩 여부)를 나타내는 변수
    is_loading: bool = False

    async def handle_search(self):
        """
        '검색' 버튼 클릭 시 실행되는 비동기 이벤트 핸들러.
        """
        # 검색어가 비어있으면 아무 작업도 수행하지 않음
        if not self.search_query.strip():
            return

        # 1. 로딩 상태 시작
        self.is_loading = True
        yield

        # 2. 실제 검색 로직 수행 (여기서는 2초 대기로 시뮬레이션)
        # 실제 애플리케이션에서는 이 부분에 Supabase DB에 RPC를 호출하는 코드가 들어갑니다.
        await asyncio.sleep(2)

        # 3. 검색 결과 생성 (시뮬레이션용 목업 데이터)
        # 실제로는 DB 조회 결과가 이 자리에 들어옵니다.
        if "reflex" in self.search_query.lower():
            self.search_results = [
                {"id": 1, "rrf_score": 0.95, "content": "Reflex는 순수 Python으로 웹 앱을 빌드할 수 있는 프레임워크입니다."},
                {"id": 2, "rrf_score": 0.87, "content": "Reflex의 상태 관리는 UI를 자동으로 업데이트하여 개발을 간소화합니다."},
                {"id": 3, "rrf_score": 0.82, "content": "rx.foreach와 rx.cond를 사용하면 동적이고 조건부적인 UI를 쉽게 만들 수 있습니다."},
            ]
        else:
            self.search_results = [] # 일치하는 결과가 없으면 빈 리스트로 설정

        # 4. 로딩 상태 종료
        self.is_loading = False
        yield

def render_search_result(result: SearchResult) -> rx.Component:
    """
    개별 검색 결과를 표시하는 카드 컴포넌트를 렌더링하는 함수.
    rx.foreach의 render_fn으로 사용됩니다.
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
            rx.heading("하이브리드 검색 엔진", size="7", align="center", margin_bottom="1em"),
            
            # 검색 입력창과 버튼
            rx.hstack(
                rx.input(
                    value=SearchState.search_query,
                    on_change=SearchState.set_search_query,
                    placeholder="검색어를 입력하세요...",
                    size="3",
                    flex_grow=1,
                ),
                rx.button(
                    "검색",
                    on_click=SearchState.handle_search,
                    is_loading=SearchState.is_loading,
                    size="3",
                ),
                spacing="2",
                width="100%",
            ),

            rx.divider(margin_y="2em"),

            # 로딩 및 결과 표시를 위한 조건부 렌더링
            rx.cond(
                SearchState.is_loading,
                # 로딩 중일 때: 스피너 표시
                rx.center(rx.spinner(size="3"), width="100%"),
                # 로딩이 아닐 때: 결과 표시
                rx.cond(
                    SearchState.search_results,
                    # 결과가 있을 때: rx.foreach로 결과 목록 렌더링
                    rx.vstack(
                        rx.foreach(
                            SearchState.search_results,
                            render_search_result,
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    # 결과가 없을 때: 메시지 표시
                    rx.center(
                        rx.text("검색 결과가 없습니다.", color_scheme="gray"),
                        width="100%",
                        height="10em"
                    ),
                ),
            ),
            spacing="4",
            width="100%",
            max_width="960px",
        ),
        padding_x="1em",
        padding_y="2em",
    )

