import os
import reflex as rx
import asyncio
import logging
from typing import List, Dict, Any
from ..agents.researcher import (
    get_sub_questions,
    run_researcher,
    write_report,
)

# --- Basic logging configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ResearchState(rx.State):
    """
    Manages the entire research process, from user input to final report generation.
    """
    # Core state variables
    main_question: str = ""
    tavily_api_key: str = ""
    sub_questions: List[str] = []
    research_results: List[Dict[str, Any]] = []
    report: str = ""

    # UI control variables
    is_generating: bool = False
    current_status: str = ""

    @rx.var
    def is_form_valid(self) -> bool:
        """Check if the form can be submitted."""
        return bool(self.main_question.strip())

    async def start_research_process(self, form_data: dict):
        """
        The main entry point to start the research, triggered by form submission.
        This runs the entire research pipeline in the background.
        """
        self.main_question = form_data.get("main_question", "").strip()

        if not self.is_form_valid:
            return

        # Reset state for a new research task
        self.is_generating = True
        self.sub_questions = []
        self.research_results = []
        self.report = ""
        self.current_status = "리서치 프로세스 시작 중..."
        
        logging.info("🚀 Starting new research process.")
        # Run the long-running research process in the background
        return ResearchState.run_background_research  # 직접 State 클래스 참조 (self 대신)

    @rx.event(background=True)
    async def run_background_research(self):
        """
        A background task to perform the research without blocking the UI.
        Each step updates the state safely using 'async with self'.
        """
        try:
            logging.info(f"Main Question: '{self.main_question}'")
            
            # Step 1: Generate Sub-questions
            async with self:
                self.current_status = "1/3 - 하위 질문 생성 중..."
            
            logging.info("Generating sub-questions...")
            sub_qs = await asyncio.to_thread(get_sub_questions, self.main_question)
            async with self:
                self.sub_questions = sub_qs
            logging.info(f"✅ Generated {len(self.sub_questions)} sub-questions: {self.sub_questions}")

            # Step 2: Run Research for each Sub-question
            async with self:
                self.current_status = f"2/3 - {len(self.sub_questions)}개의 하위 질문에 대해 리서치 진행 중..."
            
            logging.info("Starting research for all sub-questions...")
            research_tasks = [
                run_researcher(sq, self.tavily_api_key) for sq in self.sub_questions
            ]
            
            temp_results = []
            for i, task in enumerate(asyncio.as_completed(research_tasks)):
                result = await task
                temp_results.append(result)
                # Sort results to maintain the original order of sub-questions
                sorted_results = sorted(temp_results, key=lambda r: self.sub_questions.index(r['sub_question']))
                async with self:
                    self.research_results = sorted_results
                    self.current_status = f"2/3 - 리서치 완료 ({i+1}/{len(self.sub_questions)})"
                logging.info(f"({i+1}/{len(self.sub_questions)}) Research complete for: '{result['sub_question']}'")

            logging.info("✅ All research tasks completed.")

            # Step 3: Write the Final Report
            async with self:
                self.current_status = "3/3 - 최종 보고서 작성 중..."
            
            logging.info("Writing final report...")
            final_report = await asyncio.to_thread(write_report, self.research_results, self.main_question)
            async with self:
                self.report = final_report
            logging.info("✅ Final report generated.")

            async with self:
                self.current_status = "리서치 완료!"
            logging.info("🎉 Research process finished successfully.")

        except Exception as e:
            logging.error(f"An error occurred during the research process: {e}", exc_info=True)
            async with self:
                self.current_status = f"오류 발생: {e}"
        finally:
            async with self:
                self.is_generating = False
            logging.info("State `is_generating` set to False. Process ended.")