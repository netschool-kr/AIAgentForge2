# AIAgentForge/pages/collections.py

import reflex as rx
from AIAgentForge.state.collection_state import CollectionState
from AIAgentForge.components.navbar import navbar  # Navbar 임포트 추가

def render_creation_form() -> rx.Component:
    """새 컬렉션 생성을 위한 폼 컴포넌트."""
    return rx.form(
        rx.hstack(
            rx.input(
                placeholder="새 컬렉션 이름...",
                value=CollectionState.new_collection_name,
                on_change=CollectionState.set_new_collection_name, # 제어 컴포넌트
                flex_grow=1,
            ),
            rx.button(
                "생성",
                type="submit",
                is_loading=CollectionState.is_loading,
            ),
        ),
        on_submit=CollectionState.create_collection,
        width="100%",
    )
    

def render_collection_item(collection: dict) -> rx.Component:
    """단일 컬렉션 아이템을 렌더링하고, 상세 페이지로 연결되는 링크를 포함합니다."""
    return rx.link(
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.heading(collection["name"], size="5"),
                    rx.text(f"생성일: {collection['created_at']}"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.cond(
                    CollectionState.show_confirm_modal,
                    rx.dialog.root(
                        rx.dialog.content(
                            rx.dialog.title("삭제 확인"),
                            rx.dialog.description("정말로 이 컬렉션을 삭제하시겠습니까?"),
                            rx.flex(
                                rx.button("취소", on_click=CollectionState.cancel_delete),
                                rx.button("삭제", on_click=CollectionState.confirm_delete, color_scheme="red"),
                                spacing="3",
                                margin_top="16px",
                                justify="end",
                            ),
                        ),
                    ),
                ),
                rx.icon(tag="chevron_right"), # 사용자가 클릭할 수 있음을 시각적으로 암시
                align_items="center",
                width="100%",
            ),
            width="100%",
        ),
        href=f"/collections/{collection['id']}", # 동적 경로로 연결
        width="100%",
        text_decoration="none", # 링크 기본 스타일 제거
        color="inherit",
        _hover={}, # 호버 효과 제거
    )

def render_collections_list() -> rx.Component:
    """컬렉션 목록을 조건부로 렌더링합니다."""
    return rx.cond(
        CollectionState.is_loading,
        rx.center(rx.spinner(size="3")), # 로딩 중일 때 스피너 표시
        rx.cond(
            CollectionState.collections, # 컬렉션 목록이 비어있지 않을 때
            rx.vstack(
                rx.foreach(CollectionState.collections, render_collection_item),
                spacing="4",
                width="100%",
            ),
            rx.center( # 컬렉션 목록이 비어있을 때
                rx.text("생성된 컬렉션이 없습니다. 첫 번째 컬렉션을 만들어보세요!"),
                padding_y="4em",
            )
        )
    )
    
def collections_page() -> rx.Component:
    """컬렉션 관리 페이지의 메인 UI."""
    return rx.container(
        rx.vstack(
            navbar(),  # Navbar 추가
            rx.heading("내 컬렉션 관리", size="8", margin_bottom="1em"),
            render_creation_form(),
            rx.divider(margin_y="2em"),
            render_collections_list(),
            spacing="5",
            width="100%",
            max_width="60em",
            padding_top="2em",
        ),
        size="4",
    )
