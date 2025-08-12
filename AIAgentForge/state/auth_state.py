# AIAgentForge/state/auth_state.py
import reflex as rx
from .base import BaseState

class AuthState(BaseState):
    """
    Handles all authentication logic including login, logout, signup,
    and checking the authentication status on page loads.
    """

    # JWT tokens stored in browser cookies for session persistence.
    access_token: str = rx.Cookie("")
    refresh_token: str = rx.Cookie("")
    
    # State for UI feedback during auth operations.
    error_message: str = ""
    is_loading: bool = False

    @rx.var
    def user_email(self) -> str:
        """Returns the user's email if they are logged in, otherwise an empty string."""
        return self.user.email if self.user else ""

    async def check_auth(self):
        """
        페이지 로드 시 인증을 확인하고, 필요 시 토큰을 자동으로 갱신합니다.
        "실패 시 갱신(Refresh on Failure)" 전략을 사용합니다.
        """
        # 1. 쿠키에 access_token이 없으면 명백히 비로그인 상태입니다.
        if not self.access_token:
            # 만약 서버 상태가 동기화되지 않았다면(예: is_authenticated가 True), 초기화합니다.
            if self.is_authenticated:
                self._reset_auth_state()
            return rx.redirect("/login")

        try:
            # 2. access_token의 유효성을 Supabase 서버에 직접 확인합니다.
            response = await self.supabase_client.auth.get_user(self.access_token)
            if response.user:
                self.user = response.user
                self.is_authenticated = True
                yield
            else:
                # get_user가 user를 반환하지 않는 예외적인 경우
                raise Exception("User not found with the given token.")

        except Exception:
            # 3. get_user 실패: access_token이 만료되었거나 유효하지 않다는 의미입니다.
            # 이제 refresh_token으로 세션 갱신을 시도합니다.
            if not self.refresh_token:
                # 갱신 토큰조차 없으면 완전히 로그아웃 처리합니다.
                self._reset_auth_state()
                return rx.redirect("/login")

            try:
                # 4. refresh_token으로 새로운 세션(access_token + refresh_token)을 요청합니다.
                response = await self.supabase_client.auth.refresh_session(self.refresh_token)

                # 5. 세션 갱신 성공: 새로운 토큰들로 상태를 업데이트합니다 (토큰 로테이션).
                if response.session:
                    self.access_token = response.session.access_token
                    self.refresh_token = response.session.refresh_token
                    self.user = response.user
                    self.is_authenticated = True
                    yield
                else:
                    raise Exception("Session refresh did not return a session.")

            except Exception:
                # 6. 세션 갱신 실패: refresh_token도 만료되었거나 유효하지 않습니다.
                # 모든 인증 정보를 지우고 로그인 페이지로 보냅니다.
                self._reset_auth_state()
                yield rx.redirect("/login")

    def _reset_auth_state(self):
        """인증 관련 모든 상태를 깨끗하게 초기화하는 헬퍼 메서드."""
        self.access_token = ""
        self.refresh_token = ""
        self.is_authenticated = False
        self.user = None

    async def handle_login(self, form_data: dict):
        """Handles the login form submission."""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            response = self.supabase_client.auth.sign_in_with_password(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if response.session:
                # Success! Set cookies and server state.
                self.access_token = response.session.access_token
                self.refresh_token = response.session.refresh_token
                self.is_authenticated = True
                self.user = response.user
                self.is_loading = False
                # Yield the redirect event instead of returning it.
                yield rx.redirect("/")
                # Use a bare return to exit the generator.
                return
        except Exception:
            self.error_message = "이메일 또는 비밀번호가 잘못되었습니다."
        
        # This part only runs if login fails.
        self.is_loading = False
        yield

    async def handle_logout(self):
        """Logs the user out, clears all state, and redirects."""
        self.access_token = ""
        self.refresh_token = ""
        self.is_authenticated = False
        self.user = None
        # Inform Supabase to invalidate the token on the server.
        self.supabase_client.auth.sign_out()
        yield rx.redirect("/login")

    async def handle_signup(self, form_data: dict):
        """Handles the signup form submission."""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            response = self.supabase_client.auth.sign_up(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if response.user:
                # Depending on your Supabase settings, a session might be returned directly.
                if response.session:
                    # Delegate event handling to handle_login.
                    # We must iterate over the async generator and yield its events.
                    async for event in self.handle_login(form_data):
                        yield event
                    return
                else:
                    self.error_message = "회원가입 성공! 확인 이메일을 확인해주세요."
            else:
                self.error_message = "회원가입에 실패했습니다."
        except Exception as e:
            self.error_message = f"오류 발생: {getattr(e, 'message', str(e))}"
        
        self.is_loading = False
        yield
