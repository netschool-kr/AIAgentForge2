# AIAgentForge/state/base.py
import os
import reflex as rx
from supabase import create_client, Client
from gotrue.types import User
from typing import ClassVar

class BaseState(rx.State):
    """
    앱의 기본 상태입니다.
    공유 변수와 Supabase 클라이언트를 포함합니다.
    모든 다른 상태는 이 상태를 상속해야 합니다.
    """
    # 공유 인증 상태 변수.
    # 이것들은 BaseState를 상속하는 다른 상태들이 접근할 수 있도록 여기에서 정의됩니다.
    is_authenticated: bool = False
    user: User | None = None

    # 모든 상태에서 공유되는 Supabase 클라이언트 인스턴스.
    # ClassVar이므로 한 번만 초기화됩니다.
    supabase_client: ClassVar[Client] = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY")
    )