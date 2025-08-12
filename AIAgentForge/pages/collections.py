# langconnect_fullstack/pages/collections.py
import reflex as rx
from ..state.collection_state import CollectionState
from ..state.auth_state import AuthState
from AIAgentForge.components.navbar import navbar  # Navbar 임포트 추가

def collection_row(collection: dict) -> rx.Component:
    """테이블의 각 행을 렌더링하고 상세 페이지로 연결하는 컴포넌트 함수"""
    return rx.table.row(
        rx.table.cell(
            rx.link(
                collection["name"],
                href=f"/collections/{collection['id']}",
            )
        ),
        rx.table.cell(collection["created_at"]),
        rx.table.cell(
            rx.button(
                "삭제",
                on_click=lambda: CollectionState.show_confirm(collection["id"]),
                color_scheme="red"
            )
        ),
    )

@rx.page(route="/collections", on_load=[AuthState.check_auth, CollectionState.load_collections])
def collections_page() -> rx.Component:
    """컬렉션 관리 페이지 UI"""
    return rx.cond(
        AuthState.is_authenticated,
        rx.container(
            navbar(),
            rx.heading("컬렉션 관리", size="5"),
            rx.form.root(
                rx.hstack(
                    rx.input(name="name", placeholder="새 컬렉션 이름", required=True),
                    rx.button("생성", type="submit"),
                ),
                on_submit=CollectionState.create_collection,
                reset_on_submit=True,
            ),
            rx.cond(
                CollectionState.is_loading,
                rx.spinner(),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("이름"),
                            rx.table.column_header_cell("생성일"),
                            rx.table.column_header_cell("작업"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(CollectionState.collections, collection_row)
                    ),
                ),
            ),
            
            # --- 수정된 부분 ---
            # rx.cond 대신 rx.dialog.root의 open과 on_open_change 속성을 사용합니다.
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("삭제 확인"),
                    rx.dialog.description("정말로 이 컬렉션을 삭제하시겠습니까?"),
                    rx.flex(
                        rx.button(
                            "취소",
                            on_click=CollectionState.cancel_delete,
                            color_scheme="gray",
                            variant="soft",
                        ),
                        rx.button(
                            "삭제",
                            on_click=CollectionState.confirm_delete,
                            color_scheme="red"
                        ),
                        spacing="3",
                        margin_top="16px",
                        justify="end",
                    ),
                ),
                # 다이얼로그의 열림/닫힘 상태를 상태 변수와 바인딩합니다.
                open=CollectionState.show_confirm_modal,
                # 다이얼로그가 닫힐 때 (예: ESC 키, 오버레이 클릭) 상태를 업데이트합니다.
                on_open_change=CollectionState.set_show_confirm_modal,
            ),
        ),
        rx.container(
            rx.text("로그인해주세요."),
            rx.link("로그인 페이지로 이동", href="/login")
        )
    )
