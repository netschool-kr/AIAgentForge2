# AIAgentForge/pages/collection_detail.py (가칭)
import reflex as rx
from ...state.document_state import DocumentState

def render_upload_progress() -> rx.Component:
    """각 파일의 업로드 진행 상황을 동적으로 렌더링합니다."""
    return rx.vstack(
        rx.foreach(
            DocumentState.upload_progress.keys(),
            lambda filename: rx.vstack(
                rx.text(filename),
                rx.progress(value=DocumentState.upload_progress.get(filename, 0)),
                rx.text(DocumentState.upload_status.get(filename, "")),
                rx.cond(
                    DocumentState.upload_errors.get(filename),
                    rx.callout(
                        DocumentState.upload_errors.get(filename, ""),
                        icon="alert_triangle",
                        color_scheme="red",
                    ),
                ),
                width="100%",
                padding_y="0.5em",
            ),
        ),
        width="100%",
    )

def collection_detail_page() -> rx.Component:
    """컬렉션 상세 페이지 UI (업로드 기능 포함)"""
    return rx.container(
        #... (컬렉션 정보 표시 부분)
        rx.upload(
            rx.text("여기에 파일을 드래그 앤 드롭하거나 클릭하여 업로드하세요."),
            border="1px dotted rgb(107, 114, 128)",
            padding="2em",
            width="100%",
            on_drop=DocumentState.handle_upload,
            is_disabled=DocumentState.is_uploading,
        ),
        render_upload_progress(), # 동적 진행 상황 표시 부분
        #...
    )

