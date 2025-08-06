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
        Verifies authentication on page load for protected routes.
        This is the single source of truth for auth status.
        It runs every time a protected page is loaded.
        """
        # If there is no access token in the cookie, the user is not logged in.
        if not self.access_token:
            # If server state is out of sync, reset it.
            if self.is_authenticated:
                self.is_authenticated = False
                self.user = None
            yield rx.redirect("/login")
            return

        try:
            # The token exists. Verify its validity by fetching the user from Supabase.
            response = self.supabase_client.auth.get_user(self.access_token)
            self.user = response.user
            self.is_authenticated = True
            yield
        except Exception:
            # The token is invalid or expired.
            # Clear all local auth state and redirect to login.
            self.access_token = ""
            self.refresh_token = ""
            self.is_authenticated = False
            self.user = None
            yield rx.redirect("/login")

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
