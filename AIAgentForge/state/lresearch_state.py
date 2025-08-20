# AIAgentForge/state/lresearch_state.py

import reflex as rx
# build_agent_graph를 직접 임포트합니다.
from AIAgentForge.agents.lresearcher import build_agent_graph
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LResearchState(rx.State):
    """
    Local Deep Researcher 페이지의 상태를 관리합니다.
    """
    # 사용자 입력을 위한 변수
    query: str = ""
    
    # 최종 보고서를 저장할 변수
    report: str = ""
    
    # 에이전트 실행 여부를 추적하는 변수 (UI 로딩 상태 표시용)
    is_running: bool = False
    
    # 에이전트 실행 상태 메시지 (진행 상황을 표시)
    status_message: str = ""

    async def start_research(self):
        """
        사용자 입력을 받아 백그라운드에서 리서치 에이전트를 실행합니다.
        """
        if not self.query.strip():
            # 입력이 없을 경우 아무것도 하지 않음
            return
        
        # 이전 결과 초기화 및 실행 상태 업데이트
        self.is_running = True
        self.report = ""
        self.status_message = "리서치를 시작합니다... (최대 몇 분 정도 소요될 수 있습니다)"
        
        # 백그라운드 태스크로 에이전트 실행
        # UI가 멈추는 것을 방지합니다.
        return type(self).run_agent_background

    @rx.event(background=True)
    async def run_agent_background(self):
        """
        리서치 에이전트 그래프를 단계별로 실행하고 UI 상태를 업데이트합니다.
        """
        try:
            async with self:
                self.status_message = "에이전트 워크플로우를 구성합니다..."
            
            # LangGraph 워크플로우를 빌드합니다.
            graph = build_agent_graph()
            initial_state = {"query": self.query, "plan": "", "drafts": [], "critiques": [], "report": ""}

            final_state = None
            # graph.astream()을 사용하여 각 단계를 비동기적으로 순회합니다.
            # 각 단계의 출력을 스트리밍하여 UI를 실시간으로 업데이트합니다.
            async for step_output in graph.astream(initial_state):
                # step_output은 {'node_name': state_update} 형태의 딕셔너리입니다.
                node_name = list(step_output.keys())[0]
                
                # 현재 실행 중인 노드에 따라 상태 메시지를 업데이트합니다.
                async with self:
                    if node_name == "planner":
                        self.status_message = "✅ 1/3: 리서치 계획을 생성 중입니다..."
                    elif node_name == "researcher":
                        self.status_message = "✅ 2/3: 웹 검색 및 초안을 작성 중입니다..."
                    elif node_name == "reporter":
                        self.status_message = "✅ 3/3: 최종 보고서를 생성 중입니다..."
                
                # 마지막 상태를 계속해서 저장합니다.
                final_state = step_output

            # 최종 결과 추출 및 상태 업데이트
            # 마지막 노드('reporter')의 결과에서 보고서를 가져옵니다.
            report_result = final_state['reporter'].get("report", "보고서 생성에 실패했습니다.")
            
            async with self:
                self.report = report_result
                self.is_running = False
                self.status_message = "🎉 리서치가 완료되었습니다."
                
        except Exception as e:
            async with self:
                self.report = f"오류가 발생했습니다: {e}"
                self.is_running = False
                self.status_message = "오류로 인해 리서치가 중단되었습니다."
            logging.error(f"Background task error: {e}")

