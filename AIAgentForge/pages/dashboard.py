#AIAgentForge/ AIAgentForge /pages/dashboard.py:
import reflex as rx
from AIAgentForge.state.dashboard_state import DashboardState

def dashboard_page() -> rx.Component:
    """
    대시보드의 메인 페이지 UI를 정의하는 컴포넌트 함수입니다.
    """
    return rx.vstack(
        rx.heading("사용자 대시보드", size="8"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("이름"),
                    rx.table.column_header_cell("나이"),
                    rx.table.column_header_cell("역할"),
                )
            ),
            # 테이블 본문을 추가하고 상태와 연결합니다.
            rx.table.body(
                rx.foreach(
                    DashboardState.users,
                    lambda user: rx.table.row(
                        rx.table.cell(user["name"]),
                        rx.table.cell(user["age"]),
                        rx.table.cell(user["role"]),
                    ),
                )
            ),
        ),
        rx.divider(),
        # 폼 컴포넌트로 상호작용 부분을 감싸고 이벤트 핸들러를 연결합니다.
        rx.form(
            rx.hstack(
                rx.input(placeholder="이름", name="name", required=True),
                rx.input(placeholder="나이", name="age", type="number", required=True),
                rx.button("사용자 추가", type="submit"),
            ),
            on_submit=DashboardState.add_user,
            reset_on_submit=True,
        ),
        spacing="5",
        align="center",
        padding_y="2em",
    )
