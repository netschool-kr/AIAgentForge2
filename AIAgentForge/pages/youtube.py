# -*- coding: utf-8 -*-
import reflex as rx
from ..state.youtube_state import YoutubeState
from AIAgentForge.components.navbar import navbar

# --- UI 컴포넌트 정의 ---

def result_box(title: str, text: str, language: rx.Var[str] = None) -> rx.Component:
    """결과를 표시하는 스타일링된 박스 컴포넌트."""
    return rx.box(
        rx.hstack(
            rx.heading(title, size="5"),
            rx.cond(
                language,
                rx.badge(language, color_scheme="green", variant="solid"),
            ),
            align="center",
            spacing="3",
            margin_bottom="10px",
        ),
        rx.box(
            rx.markdown(text),
            width="100%",
            height="55vh", # 높이 조절
            border="1px solid #e2e8f0",
            border_radius="5",
            padding="15px",
            overflow_y="auto",
        ),
        width="100%",
    )

def youtube_page() -> rx.Component:
    """메인 페이지 UI를 정의합니다."""
    return rx.container(
        rx.vstack(
            navbar(),
            rx.heading("유튜브 영상 요약 및 번역", size="8", margin_bottom="20px"),
            
            rx.hstack(
                rx.input(
                    placeholder="https://www.youtube.com/watch?v=...",
                    value=YoutubeState.youtube_url,
                    on_change=YoutubeState.set_youtube_url,
                    is_disabled=YoutubeState.is_processing,
                    flex_grow=1,
                ),
                rx.button(
                    rx.cond(
                        YoutubeState.is_processing,
                        rx.hstack(rx.spinner(), rx.text(YoutubeState.processing_status)),
                        rx.text("요약 및 번역")
                    ),
                    on_click=YoutubeState.process_video,
                    is_disabled=YoutubeState.is_processing,
                ),
                spacing="4",
                width="100%",
            ),
            
            rx.cond(
                YoutubeState.error_message,
                rx.box(
                    rx.text(YoutubeState.error_message),
                    background_color="#FFF5F5", color="#C53030", border="1px solid #FC8181",
                    padding="10px 15px", border_radius="5", margin_top="20px", width="100%",
                )
            ),

            # 결과 표시 영역
            rx.cond(
                YoutubeState.original_script,
                rx.vstack(
                    rx.divider(margin_y="15px"),
                    rx.hstack(
                        rx.box(
                            result_box("원문 스크립트", YoutubeState.original_script, language=YoutubeState.source_language),
                            width="33.33%",
                        ),
                        rx.box(
                            result_box("번역 결과", YoutubeState.translated_script),
                            width="33.33%",
                        ),
                        rx.box(
                            result_box("요약 결과", YoutubeState.total_summary),
                            width="33.33%",
                        ),
                        spacing="4",
                        width="100%",
                        align_items="stretch",
                    ),
                    width="100%",
                )
            ),
            
            align="center",
            width="100%",
        ),
        max_width="1600px", # 전체 너비 확장
    )
