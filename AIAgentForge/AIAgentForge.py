# AIAgentForge/AIAgentForge.py

import reflex as rx
from AIAgentForge.pages.dashboard import dashboard_page
from AIAgentForge.pages.chat import chat_page # 새로 만든 chat_page를 가져옵니다.

# 애플리케이션 인스턴스를 생성합니다.
app = rx.App()

# 기존 대시보드 페이지를 루트 URL에 연결합니다.
app.add_page(dashboard_page, route="/")

# 새로운 채팅 페이지를 '/chat' URL 경로에 연결합니다.
app.add_page(chat_page, route="/chat")

