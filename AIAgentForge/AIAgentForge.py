# AIAgentForge/AIAgentForge.py
import os
from dotenv import load_dotenv
import reflex as rx
from AIAgentForge.pages.dashboard import dashboard_page
from AIAgentForge.pages.chat import chat_page  # 새로 만든 chat_page를 가져옵니다.
from AIAgentForge.pages.login import login_page      # 로그인 페이지 import
from AIAgentForge.pages.signup import signup_page    # 회원가입 페이지 import
from AIAgentForge.state.auth_state import AuthState  # 변경: AuthState import 추가 (BaseState 대신 사용)
from AIAgentForge.pages.collections import collections_page # 새로 만든 페이지 import
from AIAgentForge.state.collection_state import CollectionState  # CollectionState import 추가
from AIAgentForge.pages.collection_detail.collection_detail import collection_detail_page # 상세 페이지 import
from AIAgentForge.pages.search import search_page 
from AIAgentForge.pages.admin_page import admin_page

load_dotenv()  # .env 파일에서 환경 변수를 로드합니다.

# 애플리케이션 인스턴스를 생성합니다.
app = rx.App()

# 보호된 라우트
app.add_page(dashboard_page, route="/", on_load=AuthState.check_auth)  
app.add_page(chat_page, route="/chat", on_load=AuthState.check_auth)  
#app.add_page(collections_page, route="/collections", on_load=[AuthState.check_auth, CollectionState.load_collections]) # on_load에 load_collections 추가
app.add_page(
    collection_detail_page,
    route="/collections/[collection_id]",
    on_load=AuthState.check_auth
)

# 공개 라우트
app.add_page(login_page, route="/login")
app.add_page(signup_page, route="/signup")
app.add_page(search_page, route="/search")

app.add_page(admin_page, route="/admin", on_load=AuthState.check_admin)