#AIAgentForge/ AIAgentForge /pages/dashboard.py:
import reflex as rx
#from reflex.components.recharts import recharts
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

        # Recharts를 사용한 막대 차트 추가
        rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="age", stroke="#8884d8", fill="#8884d8"
            ),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(),
            data=DashboardState.users, # 테이블과 동일한 상태를 사용
            height=300,
            width="100%",
        ),

        
        rx.divider(),
        # 폼 컴포넌트로 상호작용 부분을 감싸고 이벤트 핸들러를 연결합니다.
        rx.form(
            rx.hstack(
                rx.input(placeholder="이름", name="name", required=True),
                rx.input(placeholder="나이", name="age", type="number", required=True),
                rx.button("사용자 추가", type="submit"),
                justify="center",
            ),
            on_submit=DashboardState.add_user,
            reset_on_submit=True,
            align="center",
        ),
        spacing="5",
        align="center",
        padding_y="2em",
    )
