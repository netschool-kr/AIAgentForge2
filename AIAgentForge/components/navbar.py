# AIAgentForge/components/navbar.py

import reflex as rx
from AIAgentForge.state.auth_state import AuthState

def navbar() -> rx.Component:
    return rx.hstack(
        rx.link("AIAgentForge", href="/", font_weight="bold"),
        rx.spacer(),
        rx.cond(
            AuthState.is_authenticated,
            # 로그인 상태일 때
            rx.hstack(
                rx.link("대시보드", href="/"),
                rx.link("컬렉션", href="/collections"), # 컬렉션 페이지 링크 추가
                #rx.link("검색", href="/search"),
                rx.link("채팅", href="/chat"),
                rx.link("유튜브", href="/youtube"),
                rx.link("블로그", href="/blog"),
                rx.link("리서치", href="/research"),
                #rx.link("l리서치", href="/lresearch"),
                rx.cond(
                    AuthState.role == "admin",
                    rx.link("관리자 패널", href="/admin"),
                ),
                rx.spacer(),
                rx.text(AuthState.user.email),
                rx.button("로그아웃", on_click=AuthState.handle_logout),
                spacing="4",
            ),
            # 비로그인 상태일 때
            rx.hstack(
                rx.link("로그인", href="/login"),
                rx.link("회원가입", href="/signup"),
                spacing="4",
            )
        ),
        position="sticky",
        top="0",
        padding="1em",
        width="100%",
        z_index="10",
        background_color=rx.color("gray", 2),
    )