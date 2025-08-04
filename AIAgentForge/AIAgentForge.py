#AIAgentForge/AIAgentForge/AIAgentForge.py:

import reflex as rx
from AIAgentForge.pages.dashboard import dashboard_page

# 애플리케이션 인스턴스를 생성합니다.
# 테마, 스타일시트 등 앱 전반의 설정을 여기서 할 수 있습니다.
app = rx.App()

# 페이지 컴포넌트를 URL 경로에 추가(라우팅)합니다.
# 여기서는 루트 URL("/")에 dashboard_page를 연결합니다.
app.add_page(dashboard_page, route="/")
