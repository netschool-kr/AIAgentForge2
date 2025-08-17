# -*- coding: utf-8 -*-
import os
import reflex as rx
from ..state.youtube_state import YoutubeState # state 파일에서 YoutubeState를 가져옵니다.
from AIAgentForge.components.navbar import navbar  # Navbar 임포트 추가

# --- 중요: API 키 설정 ---
# 이 스크립트를 실행하기 전에 터미널에서 아래와 같이 환경 변수를 설정해주세요.
# export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
# export LANGCHAIN_API_KEY="YOUR_LANGCHAIN_API_KEY"


# --- Reflex UI (웹 페이지 구성) ---

def result_box(title: str, text: str) -> rx.Component:
    """결과를 표시하는 스타일링된 박스 컴포넌트."""
    return rx.box(
        rx.heading(title, size="5", margin_bottom="10px"),
        rx.box(
            rx.markdown(text),
            width="100%",
            height="60vh",
            border="1px solid #e2e8f0",
            border_radius="5",
            padding="15px",
            overflow_y="auto",
            _hover={"border_color": "#cbd5e0"},
        ),
        width="100%",
    )

def youtube_page() -> rx.Component:
    """메인 페이지 UI를 정의합니다."""
    return rx.container(
        rx.vstack(
            navbar(),
            rx.heading("번역하고 싶은 유튜브 영상의 URL을 입력하세요.", size="8", margin_bottom="10px"),
                        
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
                        rx.spinner(),
                        rx.text("번역하기")
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
                    background_color="#FFF5F5",
                    color="#C53030",
                    border="1px solid #FC8181",
                    padding="10px 15px",
                    border_radius="5",
                    margin_top="20px",
                    width="100%",
                )
            ),

            rx.cond(
                YoutubeState.original_script,
                rx.hstack(
                    # 각 result_box를 너비 50%를 가진 box로 감싸서 크기를 고정합니다.
                    rx.box(
                        result_box(f"원문 스크립트 (언어:{YoutubeState.source_language})", YoutubeState.original_script),
                        width="50%",
                    ),
                    rx.box(
                        result_box("번역 결과", YoutubeState.translated_script),
                        width="50%",
                    ),
                    spacing="3",
                    width="100%",
                    align_items="stretch", # 박스 높이를 동일하게 맞춤
                ),
            ),
            
            align="center",
            width="100%",
        ),
        #max_width="900px",
        #padding="20px",
        #margin_top="10px",
    )