# AIAgentForge/state/base.py
import os
import reflex as rx
from supabase import create_client, Client
from gotrue.types import User
from typing import ClassVar
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient
# --- [삭제된 부분] ---
# 순환 참조를 유발하는 최상위 import를 제거합니다.
# from .auth_state import AuthState

class BaseState(rx.State):
    """
    앱의 기본 상태입니다.
    공유 변수와 Supabase 클라이언트를 포함합니다.
    모든 다른 상태는 이 상태를 상속해야 합니다.
    """
    is_authenticated: bool = False
    user: User | None = None
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    load_dotenv()

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

    supabase_client: ClassVar[Client] = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    async def _get_authenticated_client(self) -> SyncPostgrestClient:
        """인증된 Postgrest 클라이언트를 반환합니다."""
        # --- [수정된 부분] ---
        # 함수 내에서 AuthState를 import하여 순환 참조를 방지합니다.
        from .auth_state import AuthState
        
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            raise Exception("사용자가 인증되지 않았습니다.")
        return SyncPostgrestClient(
            f"{self.SUPABASE_URL}/rest/v1",
            headers={
                "apikey": self.SUPABASE_KEY,
                "Authorization": f"Bearer {auth_state.access_token}",
            }
        )

    async def _get_supabase_client(self) -> Client:
        """인증된 Supabase 클라이언트를 반환합니다."""
        # --- [수정된 부분] ---
        # 함수 내에서 AuthState를 import하여 순환 참조를 방지합니다.
        from .auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            raise Exception("사용자가 인증되지 않았습니다.")
        client: Client = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
        client.auth.set_session(auth_state.access_token, '')
        return client
