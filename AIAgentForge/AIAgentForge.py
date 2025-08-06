# AIAgentForge/AIAgentForge.py
import os
from dotenv import load_dotenv
import reflex as rx
from AIAgentForge.pages.dashboard import dashboard_page
from AIAgentForge.pages.chat import chat_page # 새로 만든 chat_page를 가져옵니다.
from AIAgentForge.pages.login import login_page      # 로그인 페이지 import
from AIAgentForge.pages.signup import signup_page    # 회원가입 페이지 import
from AIAgentForge.state.base import BaseState

load_dotenv() #.env 파일에서 환경 변수를 로드합니다.

# 애플리케이션 인스턴스를 생성합니다.
app = rx.App()

# 기존 대시보드 페이지를 루트 URL에 연결합니다.
app.add_page(dashboard_page, route="/", on_load=BaseState.check_auth)

# 새로운 채팅 페이지를 '/chat' URL 경로에 연결합니다.
app.add_page(chat_page, route="/chat", on_load=BaseState.check_auth)

# 신규 인증 라우트 추가
app.add_page(login_page, route="/login")
app.add_page(signup_page, route="/signup")
