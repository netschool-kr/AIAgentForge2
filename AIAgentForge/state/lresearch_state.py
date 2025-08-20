# AIAgentForge/state/lresearch_state.py

import reflex as rx
from AIAgentForge.agents.lresearcher import run_research_agent
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
    
    # 에이전트 실행 상태 메시지
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
        yield type(self).run_agent_background

    @rx.event(background=True)
    async def run_agent_background(self):
        """
        실제 리서치 에이전트 함수를 호출하는 백그라운드 작업.
        `run_research_agent`는 동기 함수이므로, 그대로 호출합니다.
        """
        
        try:
            logging.info(f"run_agent_background 0: '{self.query}'")

            # 동기 함수를 직접 호출
            report_result = run_research_agent(self.query)
            
            logging.info(f"run_agent_background 1: '{report_result}'")
            # 작업이 완료되면 UI를 업데이트하기 위해 프론트엔드 이벤트를 호출
            async with self:
                self.report = report_result
                self.is_running = False
                self.status_message = "리서치가 완료되었습니다."
                
        except Exception as e:
            async with self:
                self.report = f"오류가 발생했습니다: {e}"
                self.is_running = False
                self.status_message = "오류로 인해 리서치가 중단되었습니다."
            logging.error(f"Background task error: {e}")
