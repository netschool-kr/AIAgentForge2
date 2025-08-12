# AIAgentForge/pages/collection_detail/collection_detail.py
import reflex as rx
from ...state.document_state import DocumentState
from ...state.auth_state import AuthState

def render_upload_progress() -> rx.Component:
    """각 파일의 업로드 진행 상황을 동적으로 렌더링합니다."""
    return rx.cond(
        DocumentState.is_uploading,
        rx.vstack(
            rx.foreach(
                DocumentState.upload_status.keys(),
                lambda filename: rx.vstack(
                    rx.hstack(
                        rx.text(filename, as_="b"),
                        rx.text(DocumentState.upload_status.get(filename, "")),
                        spacing="3",
                    ),
                    rx.progress(value=DocumentState.upload_progress.get(filename, 0), width="100%"),
                    rx.cond(
                        DocumentState.upload_errors.get(filename),
                        rx.callout(
                            DocumentState.upload_errors.get(filename, ""),
                            icon="alert_triangle",
                            color_scheme="red",
                            width="100%",
                        ),
                    ),
                    width="100%",
                    padding_y="0.5em",
                ),
            ),
            width="100%",
            padding_top="1em",
        ),
    )

def document_list() -> rx.Component:
    """DB에 저장된 문서 목록을 표시합니다."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("문서 이름"),
                rx.table.column_header_cell("생성일"),
                rx.table.column_header_cell("작업"),
            )
        ),
        rx.table.body(
            rx.foreach(
                DocumentState.documents,
                lambda doc: rx.table.row(
                    rx.table.cell(doc["name"]),
                    rx.table.cell(doc["created_at"]),
                    rx.table.cell(
                        rx.button(
                            "삭제", 
                            color_scheme="red", 
                            variant="soft",
                            on_click=DocumentState.delete_document(doc["id"])  # 삭제 핸들러 추가 (doc에 "id" 키가 있다고 가정)
                        )
                    ),                    
                )
            )
        ),
        width="100%",
    )

@rx.page(
    route="/collections/[collection_id]",
    on_load=[AuthState.check_auth, DocumentState.load_documents_on_page_load]#, lambda: DocumentState.set_process_document(True)]
)
def collection_detail_page() -> rx.Component:
    """컬렉션 상세 페이지 UI (업로드 기능 포함)"""
    return rx.container(
        rx.heading(f"컬렉션: {DocumentState.collection_name}", size="5", margin_bottom="1em"),
        
        rx.hstack(
            # rx.checkbox(
            #     "Upload",
            #     is_checked=DocumentState.upload_document,
            #     default_checked=True,
            #     on_change=DocumentState.toggle_upload_document,
            # ),
            # rx.checkbox(
            #     "Process",
            #     is_checked=DocumentState.process_document,
            #     default_checked=True,
            #     on_change=DocumentState.toggle_process_document,
            # ),
            spacing="4",
            margin_bottom="1em",
        ),
        
        rx.upload(
            rx.vstack(
                rx.button("파일 선택", type="button"),
                rx.text("또는 여기에 파일을 드래그 앤 드롭하세요."),
                align="center",
            ),
            id="upload",
            border="1px dotted rgb(107, 114, 128)",
            padding="2em",
            width="100%",
            is_disabled=DocumentState.is_uploading,
            on_drop=DocumentState.handle_upload(
                rx.upload_files(
                    upload_id="upload",
                    # on_upload_progress 핸들러가 없으므로 이 라인을 제거합니다.
                )
            ),
        ),  
              
        render_upload_progress(),
        rx.divider(margin_y="2em"),
        rx.heading("업로드된 문서", size="4", margin_bottom="1em"),
        rx.cond(
            DocumentState.is_loading,
            rx.spinner(),
            document_list()
        ),
    )
