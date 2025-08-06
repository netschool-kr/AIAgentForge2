# AIAgentForge/state/base.py
import os
import reflex as rx
from supabase import create_client, Client
from gotrue.types import User
from typing import ClassVar

class BaseState(rx.State):
    """
    The base state for the app.
    Contains shared variables and the Supabase client.
    All other states should inherit from this state.
    """
    # Shared authentication state variables.
    # These are defined here so other states inheriting from BaseState can access them.
    is_authenticated: bool = False
    user: User | None = None

    # Supabase client instance, shared across all states.
    # It is a ClassVar, so it's initialized only once.
    supabase_client: ClassVar[Client] = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY")
    )
