# AIAgentForge/state/auth_state.py

import reflex as rx
from gotrue.types import User
from .base import BaseState
import random
import time

class AuthState(BaseState):
    """인증과 관련된 모든 상태와 로직을 관리합니다."""

    # 기본 상태 변수 (Base Vars)
    is_authenticated: bool = False
    user: User | None = None
    error_message: str = ""
    is_loading: bool = False
    
    @rx.var
    def user_email(self) -> str:
        return self.user.email if self.user else ""

    #@rx.var
    #def auth_status(self) -> str:
    #    return "Authenticated" if self.is_authenticated else "Not Authenticated"

    # JWT 토큰을 저장할 rx.Cookie 타입의 상태 변수
    access_token: str = rx.Cookie("")
    refresh_token: str = rx.Cookie("")

    async def handle_login(self, form_data: dict):
        """로그인 폼 제출을 처리하는 이벤트 핸들러."""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            # supabase_client는 BaseState에 정의된 전역 클라이언트 인스턴스라고 가정
            response = self.supabase_client.auth.sign_in_with_password(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if response.session:
                self.access_token = response.session.access_token
                self.refresh_token = response.session.refresh_token
                self.is_authenticated = True
                self.user = response.user
                self.is_loading = False  # 성공 시 로딩 종료
                yield  # Force state delta sync here
                #yield rx.redirect("/")
                yield rx.redirect(f"/?reload={time.time()}")
                #yield rx.redirect(f"/?reload={random.random()}")
                #yield rx.window().location.assign("/")  # 또는 yield rx.window().location.replace("/")  # Instead of rx.redirect("/")
            else:
                # 이 경우는 거의 발생하지 않지만, 방어적으로 코딩
                self.error_message = "로그인에 실패했습니다. 다시 시도해주세요."

        except Exception as e:
            self.error_message = "이메일 또는 비밀번호가 잘못되었습니다."
        
        finally:
            self.is_loading = False
            yield  # 에러 발생 시 상태 업데이트를 위해 yield 추가
            
    async def handle_signup(self, form_data: dict):
        """회원가입 폼 제출을 처리하는 이벤트 핸들러."""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            # supabase_client는 BaseState에 정의된 전역 클라이언트 인스턴스라고 가정
            response = self.supabase_client.auth.sign_up(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if response.user:
                if response.session:  # 자동 확인이 활성화된 경우 세션이 반환될 수 있음
                    self.access_token = response.session.access_token
                    self.refresh_token = response.session.refresh_token
                    self.is_authenticated = True
                    self.user = response.user
                    self.is_loading = False
                    yield rx.redirect("/")
                else:
                    # 이메일 확인이 필요한 경우
                    self.error_message = "회원가입 성공! 확인 이메일을 확인해주세요."
                    self.is_loading = False
                    yield rx.redirect("/login")  # 로그인 페이지로 리디렉션 또는 메시지 표시
            else:
                self.error_message = "회원가입에 실패했습니다. 다시 시도해주세요."

        except Exception as e:
            self.error_message = f"오류 발생: {str(e)}"
        
        finally:
            self.is_loading = False
            yield  # 상태 업데이트를 위해 yield 추가
            
    async def handle_logout(self):
        """로그아웃을 처리하고 모든 인증 상태를 초기화합니다."""
        self.is_loading = True
        yield

        # API 호출과 상태 초기화를 모두 수행
        await self.supabase_client.auth.sign_out()
        self.access_token = ""
        self.refresh_token = ""
        self.is_authenticated = False
        self.user = None
        
        self.is_loading = False
        yield  # Optional: Yield here to ensure the final state update (e.g., loading indicator) is sent before redirect
        yield rx.redirect("/login")
            