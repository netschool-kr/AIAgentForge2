# -*- coding: utf-8 -*-
import os
import re
from typing import TypedDict, Literal
from uuid import uuid4

# LangChain 및 LangGraph 관련 라이브러리
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# 유튜브 자막 추출 라이브러리
from youtube_transcript_api import YouTubeTranscriptApi

# --- 1. 환경 설정 및 LLM 초기화 ---

def setup_environment():
    """API 키 및 LangChain 추적 환경 변수를 설정합니다."""
    # --- 중요 ---
    # 아래 "" 안에 실제 API 키를 입력하거나, 시스템 환경 변수로 설정해주세요.
    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
    os.environ["LANGCHAIN_API_KEY"] = "YOUR_LANGCHAIN_API_KEY"

    if os.environ.get("LANGCHAIN_API_KEY"):
        unique_id = uuid4().hex[0:8]
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = f"YouTube Script Processor - {unique_id}"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        print("✅ LangSmith 추적이 활성화되었습니다.")

# LLM 및 프롬프트는 한 번만 초기화하여 재사용합니다.
llm = ChatOpenAI(model="gpt-4o", temperature=0)

translation_prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 한국어로 번역하는 번역 전문가야. 다음 내용을 한국어로 번역해줘."),
    MessagesPlaceholder(variable_name="messages"),
])

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", """
당신은 전문적인 요약가입니다. 사용자가 제공하는 전체 텍스트를 아래 형식과 지침에 따라 요약하십시오.

[목표]
- 주어진 텍스트의 핵심 내용을 미리 정의된 '목차 항목' 순서에 따라 요약합니다.
- 불필요한 문장은 생략하고, 중요한 정보만 간결하게 정리합니다.
- 항목별 요약 길이는 핵심에 따라 유동적으로 조절하되, 과도한 설명은 피합니다.
- 항목별 요약을 생성하기 전에 먼저 상단에 일차적으로 목차를 정리합니다.

[출력 포맷 예시]

목차
1. 목차 1
2. 목차 2
3. 목차 3

1. 항목 제목
· 핵심 요점 1
· 핵심 요점 2

2. 항목 제목
· 핵심 요점 1
· 핵심 요점 2
· 핵심 요점 3

(이후 목차 항목 순서대로 계속)

[중요 지침]
- 항목이 텍스트에 명확히 언급되지 않으면 해당 항목은 생략하지 말고 관련된 추론 가능한 내용을 바탕으로 간단히 요약합니다.
- 한 항목에 여러 개의 요점이 있을 경우, 각 요점을 줄바꿈으로 구분하여 나열하십시오.

지금부터 입력되는 텍스트에 대해 위 포맷으로 요약하십시오.
    """),
    MessagesPlaceholder(variable_name="messages"),
])

translation_chain = translation_prompt | llm
summary_chain = summary_prompt | llm

# --- 2. 핵심 기능 함수 정의 ---

def get_script_from_youtube(url: str) -> tuple[str, str]:
    """유튜브 URL에서 자막 텍스트와 언어 코드를 추출합니다."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if not match:
        raise ValueError("유효한 유튜브 영상 URL이 아닙니다.")
    video_id = match.group(1)

    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    available_langs = {t.language_code: t for t in transcript_list}
    
    preferred_order = ['ko', 'en'] + list(available_langs.keys())
    
    for lang in preferred_order:
        if lang in available_langs:
            selected_transcript = available_langs[lang]
            transcript_data = selected_transcript.fetch()
            full_script = " ".join(entry['text'] for entry in transcript_data).strip()
            return full_script, lang
            
    raise Exception("사용 가능한 자막이 없습니다.")

def translate_script_to_korean(script: str) -> str:
    """주어진 스크립트를 한국어로 번역합니다."""
    print("\n--- 번역 시작 ---")
    translated_script = ""
    request = HumanMessage(content=script)
    for chunk in translation_chain.stream({"messages": [request]}):
        print(chunk.content, end="", flush=True)
        translated_script += chunk.content
    print("\n--- 번역 종료 ---\n")
    return translated_script

def summarize_script(script: str) -> str:
    """주어진 스크립트를 요약합니다."""
    print("\n--- 요약 시작 ---")
    summary = ""
    request = HumanMessage(content=script)
    for chunk in summary_chain.stream({"messages": [request]}):
        print(chunk.content, end="", flush=True)
        summary += chunk.content
    print("\n--- 요약 종료 ---\n")
    return summary

# --- 3. LangGraph 워크플로우 정의 ---

class GraphState(TypedDict):
    """LangGraph의 상태를 정의합니다."""
    input_url: str
    original_script: str
    translated_kor_script: str
    lang_code: str
    total_summary: str

# LangGraph 노드(Node) 정의
def extract_script_node(state: GraphState) -> dict:
    """URL에서 스크립트를 추출하는 노드."""
    print(f"\n[ 1. URL에서 스크립트 추출 ]\nURL: {state['input_url']}")
    script, lang_code = get_script_from_youtube(state['input_url'])
    return {
        "original_script": script,
        "lang_code": lang_code,
        "translated_kor_script": script if lang_code == 'ko' else ""
    }

def translate_node(state: GraphState) -> dict:
    """스크립트를 한국어로 번역하는 노드."""
    print("\n[ 2. 스크립트 번역 ]")
    translated_script = translate_script_to_korean(state['original_script'])
    return {"translated_kor_script": translated_script}

def summarize_node(state: GraphState) -> dict:
    """번역된 스크립트를 요약하는 노드."""
    print("\n[ 3. 스크립트 요약 ]")
    summary = summarize_script(state['translated_kor_script'])
    return {"total_summary": summary}

def language_branching(state: GraphState) -> Literal["summarize_node", "translate_node"]:
    """언어 코드에 따라 다음 단계를 결정하는 분기점."""
    if state['lang_code'] == "ko":
        print("--- 분기: 한국어 스크립트 -> 요약으로 이동 ---")
        return "summarize_node"
    else:
        print(f"--- 분기: {state['lang_code']} 스크립트 -> 번역으로 이동 ---")
        return "translate_node"

def build_graph():
    """LangGraph 워크플로우를 구성하고 컴파일합니다."""
    workflow = StateGraph(GraphState)
    workflow.add_node("extract_script_node", extract_script_node)
    workflow.add_node("translate_node", translate_node)
    workflow.add_node("summarize_node", summarize_node)

    workflow.set_entry_point("extract_script_node")
    workflow.add_conditional_edges("extract_script_node", language_branching)
    workflow.add_edge("translate_node", "summarize_node")
    workflow.add_edge("summarize_node", END)
    
    return workflow.compile()

# --- 4. 메인 실행 로직 ---

if __name__ == "__main__":
    setup_environment()
    
    # LangGraph 워크플로우 빌드
    app = build_graph()

    # 처리할 유튜브 URL 리스트
    urls_to_process = [
        "https://www.youtube.com/watch?v=hciNKcLwSes", # 영어
        "https://www.youtube.com/watch?v=CLiS-AnRphI", # 한국어
        "https://www.youtube.com/watch?v=AzfNSmYGo1s", # 일본어
    ]

    for i, url in enumerate(urls_to_process):
        print(f"\n{'='*50}\n[ 영상 {i+1}/{len(urls_to_process)} 처리 시작 ]")
        inputs = {"input_url": url}
        final_summary = ""
        
        # 비동기 스트림으로 그래프 실행
        # for event in app.stream(inputs):
        #     for key, value in event.items():
        #         if "total_summary" in value:
        #             final_summary = value["total_summary"]
        
        # 마지막 결과만 필요한 경우 invoke 사용
        final_state = app.invoke(inputs)
        final_summary = final_state.get("total_summary", "요약 결과 없음")

        print(f"\n[ 최종 요약 결과 ]\n{final_summary}")
        
        # 결과를 파일로 저장
        filename = f"summary_{i+1}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_summary)
        print(f"✅ 결과가 {filename} 파일로 저장되었습니다.")

    print(f"\n{'='*50}\n모든 영상 처리가 완료되었습니다.")

