# AIAgentForge/state/base.py
import os
import reflex as rx
from supabase import create_client, Client  # Supabase 클라이언트 import 추가
from gotrue.types import User
from typing import ClassVar

class BaseState(rx.State):
    """
    모든 상태 클래스의 기반이 되는 기본 상태입니다.
    애플리케이션 전역에서 사용될 상태 변수나 이벤트 핸들러를 여기에 정의할 수 있습니다.
    """
    # AuthState에서 정의한 변수들을 BaseState에서도 접근할 수 있도록 선언
    is_authenticated: bool = False
    user: User | None = None
    access_token: str = rx.Cookie("")
    refresh_token: str = rx.Cookie("")

    # Supabase 클라이언트 인스턴스 추가 (클래스 변수로 전역 사용)
    supabase_client: ClassVar[Client] = create_client(
        os.getenv("SUPABASE_URL"),  # .env에서 URL 불러오기
        os.getenv("SUPABASE_ANON_KEY")   # .env에서 키 불러오기
    )

    async def check_auth(self):
        """페이지 로드 시 사용자의 인증 상태를 검증합니다."""
        # 현재 Reflex 세션 내에서 이미 인증 확인이 끝났다면, 불필요한 API 호출을 생략합니다.
        if self.is_authenticated:
            return  # 또는 yield None으로 대체 가능

        # 쿠키에 access_token이 없으면 즉시 로그인 페이지로 리디렉션합니다.
        if not self.access_token:
            yield rx.redirect("/login")
            return  # yield 후 return으로 함수 종료

        try:
            # 가장 중요한 단계: 토큰을 서버로 보내 유효성을 검증합니다.
            # supabase_client는 앱 초기화 시 생성된 전역 클라이언트입니다.
            response = self.supabase_client.auth.get_user(self.access_token)
            self.user = response.user
            self.is_authenticated = True
            yield  # 상태 업데이트를 UI에 반영 (선택적)
        except Exception:
            # 토큰이 유효하지 않거나(위조) 만료된 경우
            # 안전을 위해 모든 토큰을 삭제하고 로그인 페이지로 보냅니다.
            self.access_token = ""
            self.refresh_token = ""
            self.is_authenticated = False
            self.user = None
            yield rx.redirect("/login")