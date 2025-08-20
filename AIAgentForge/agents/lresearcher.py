# AIAgentForge/utils/research_agent.py

import os
from langchain_community.chat_models import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# .env 파일에서 환경 변수 로드
load_dotenv()

# Tavily API 키 설정 확인
if os.getenv("TAVILY_API_KEY") is None:
    raise ValueError("TAVILY_API_KEY 환경 변수가 설정되지 않았습니다.")

# --- 모델 및 도구 설정 ---
# 로컬 LLM (Llama 3) 초기화
# Ollama가 설치되어 있고 llama3 모델이 다운로드되어 있어야 합니다.
# 터미널에서 `ollama run llama3` 실행 확인
local_llm = ChatOllama(model="llama3", temperature=0)

# 웹 검색 도구 초기화
search_tool = TavilySearchResults(max_results=3)

# --- LangGraph 상태 정의 ---
class AgentState(TypedDict):
    """
    그래프의 상태를 정의하는 TypedDict.
    - query: 사용자의 초기 질문
    - plan: 리서치 계획
    - drafts: 각 하위 질문에 대한 리서치 결과 초안 리스트
    - critques: 초안에 대한 비평
    - report: 최종 보고서
    """
    query: str
    plan: str
    drafts: List[str]
    critiques: List[str]
    report: str

# --- 프롬프트 템플릿 정의 ---

# 1. 계획 생성 프롬프트
planner_prompt = ChatPromptTemplate.from_template(
    """당신은 전문적인 리서처입니다. 사용자의 질문에 대해 심층적인 답변을 제공하기 위한 리서치 계획을 단계별로 작성해주세요.
각 단계는 명확하고 실행 가능해야 합니다.

사용자 질문: {query}

리서치 계획:"""
)

# 2. 리서치 초안 작성 프롬프트
draft_prompt = ChatPromptTemplate.from_template(
    """당신은 리서치 어시스턴트입니다. 다음 질문에 대해 제공된 컨텍스트 정보를 바탕으로 상세한 답변 초안을 작성해주세요.
답변은 포괄적이고 잘 구성되어야 합니다.

질문: {query}
컨텍스트: {context}

답변 초안:"""
)

# 3. 최종 보고서 작성 프롬프트
report_prompt = ChatPromptTemplate.from_template(
    """당신은 수석 편집자입니다. 다음 리서치 초안들을 종합하여 하나의 일관되고 상세한 최종 보고서를 작성해주세요.
보고서는 서론, 본론, 결론의 구조를 갖추어야 하며, 모든 정보가 정확하게 통합되어야 합니다.

리서치 초안들:
{drafts}

최종 보고서:"""
)

# 4. 비평 및 개선 방향 제시 프롬프트
critique_prompt = ChatPromptTemplate.from_template(
    """당신은 비평가입니다. 다음 리서치 초안을 검토하고, 보고서의 품질을 향상시키기 위한 구체적인 개선 방안을 제시해주세요.
사실 확인, 깊이, 명확성 측면에서 부족한 점을 지적해주세요.

리서치 초안:
{draft}

비평 및 개선 제안:"""
)


# --- LangGraph 노드(Node) 함수 정의 ---

def plan_step(state: AgentState):
    """리서치 계획을 생성하는 노드"""
    logging.info("--- 리서치 계획 생성 중 ---")
    planner = planner_prompt | local_llm | StrOutputParser()
    plan = planner.invoke({"query": state["query"]})
    return {"plan": plan}

def research_step(state: AgentState):
    """계획에 따라 웹 검색을 수행하고 초안을 작성하는 노드"""
    print("--- 웹 검색 및 초안 작성 중 ---")
    plan_steps = state["plan"].strip().split("\n")
    drafts = []
    for step in plan_steps:
        if not step:
            continue
        logging.info(f"  - 검색 주제: {step}")
        # 웹 검색 수행
        search_results = search_tool.invoke(step)
        context = "\n".join([res["content"] for res in search_results])
        
        # 초안 생성
        draft_generator = draft_prompt | local_llm | StrOutputParser()
        draft = draft_generator.invoke({"query": step, "context": context})
        drafts.append(draft)
        logging.info(f"  - 초안 생성 완료")
    return {"drafts": drafts}

def report_step(state: AgentState):
    """초안들을 종합하여 최종 보고서를 생성하는 노드"""
    logging.info("--- 최종 보고서 생성 중 ---")
    drafts_text = "\n\n---\n\n".join(state["drafts"])
    report_generator = report_prompt | local_llm | StrOutputParser()
    report = report_generator.invoke({"drafts": drafts_text})
    return {"report": report}

# --- 그래프 구성 ---
def build_agent_graph():
    """
    LangGraph를 사용하여 리서치 에이전트의 워크플로우를 구성합니다.
    """
    workflow = StateGraph(AgentState)

    # 노드 추가
    workflow.add_node("planner", plan_step)
    workflow.add_node("researcher", research_step)
    workflow.add_node("reporter", report_step)

    # 엣지(Edge) 추가 (노드 간의 연결)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "reporter")
    workflow.add_edge("reporter", END)

    # 그래프 컴파일
    return workflow.compile()

# --- 메인 실행 함수 ---
def run_research_agent(query: str) -> str:
    """
    사용자 질문을 받아 리서치 에이전트를 실행하고 최종 보고서를 반환합니다.
    """
    try:
        
        graph = build_agent_graph()
        initial_state = {"query": query, "plan": "", "drafts": [], "critiques": [], "report": ""}
        
        logging.info(f"리서치 시작: '{query}'")
        final_state = graph.invoke(initial_state)
        logging.info("--- 리서치 완료 ---")
        
        return final_state.get("report", "보고서 생성에 실패했습니다.")
    except Exception as e:
        logging.info(f"에이전트 실행 중 오류 발생: {e}")
        return f"오류가 발생했습니다: {e}"

if __name__ == '__main__':
    # 테스트용 실행 코드
    test_query = "LLM 에이전트의 최신 연구 동향은 무엇인가?"
    report = run_research_agent(test_query)
    print("\n\n===== 최종 보고서 =====")
    print(report)
