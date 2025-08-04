#AIAgentForge/AIAgentForge/state/dashboard_state.py:

from.base import BaseState

class DashboardState(BaseState):
    """
    대시보드 페이지의 상태를 관리하는 클래스입니다.
    대시보드와 관련된 모든 변수(vars)와 이벤트 핸들러(event handlers)는
    이 클래스 내에 정의됩니다.
    """
    # 사용자 목록을 저장할 기본 변수(Base Var).
    # 초기 데이터로 두 명의 사용자를 하드코딩합니다.
    users: list[dict] = [
        {"name": "존 도", "age": 30, "role": "개발자"},
        {"name": "제인 도", "age": 28, "role": "디자이너"},
    ]

