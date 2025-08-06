#AIAgentForge/pages/chat.py

import reflex as rx
from AIAgentForge.state.chat_state import ChatState
from AIAgentForge.components.chat_bubble import chat_bubble
from AIAgentForge.components.navbar import navbar  # Navbar 임포트 추가

def action_bar() -> rx.Component:
    """사용자 입력을 받는 하단의 액션 바 컴포넌트입니다."""
    return rx.center(
        rx.vstack(
            rx.form(
                rx.hstack(
                    rx.input(
                        placeholder="질문을 입력하세요...",
                        value=ChatState.question,
                        on_change=ChatState.set_question,
                        flex_grow=1,
                    ),
                    rx.button("전송", type="submit"),
                ),
                on_submit=ChatState.answer,
                reset_on_submit=True,
                width="100%",
            ),
            width="60%",
            padding_bottom="2em",
            padding_top="1em"
        ),
        position="sticky",
        bottom="0",
        background_color=rx.color("gray", 2),
        width="100%",
    )

def chat_page() -> rx.Component:
    """
    채팅 페이지의 메인 UI를 정의하는 컴포넌트 함수입니다.
    """
    return rx.vstack(
        navbar(),  # Navbar 추가
        rx.box(
            # rx.foreach를 사용하여 chat_history 리스트를 순회하며
            # 각 메시지에 대해 chat_bubble 컴포넌트를 렌더링합니다.
            rx.foreach(ChatState.chat_history, chat_bubble),
            width="100%",
            padding_x="2em",
            padding_top="2em"
        ),
        rx.spacer(), # 채팅 내용과 액션 바 사이의 공간을 채웁니다.
        action_bar(),
        align="center",
        width="100%",
        height="100vh", # 전체 화면 높이를 차지하도록 설정
    )
