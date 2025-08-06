# AIAgentForge/pages/signup.py

import reflex as rx

from AIAgentForge.state.auth_state import AuthState


def signup_page() -> rx.Component:
    """회원가입 페이지 UI를 정의합니다."""
    return rx.center(
        rx.vstack(
            rx.heading("회원가입", size="8"),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="이메일",
                        name="email",
                        type="email",
                        required=True,
                    ),
                    rx.input(
                        placeholder="비밀번호",
                        name="password",
                        type="password",
                        required=True,
                    ),
                    # 비밀번호 확인 필드 추가
                    rx.input(
                        placeholder="비밀번호 확인",
                        name="password_confirm",
                        type="password",
                        required=True,
                    ),
                    rx.button(
                        "회원가입",
                        type="submit",
                        is_loading=AuthState.is_loading,
                        width="100%",
                    ),
                    spacing="4",
                ),
                # on_submit 핸들러를 handle_signup으로 연결
                on_submit=AuthState.handle_signup,
            ),
            # 에러 메시지가 있을 때만 조건부로 렌더링
            rx.cond(
                AuthState.error_message != "",
                rx.callout(
                    AuthState.error_message,
                    icon="alert_triangle",
                    color_scheme="red",
                    width="100%",
                    margin_top="1em",
                ),
            ),
            # 로그인 페이지로 이동하는 링크
            rx.text(
                "이미 계정이 있으신가요? ",
                rx.link("로그인", href="/login"),
                " 하세요.",
                margin_top="1em",
            ),
            spacing="5",
            align="center",
            width="25em",
        ),
        height="100vh",
    )