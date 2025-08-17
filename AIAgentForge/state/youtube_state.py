# -*- coding: utf-8 -*-
import os
import re
import reflex as xt
from typing import Tuple

# LangChain 및 LLM 관련 라이브러리
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# 유튜브 자막 추출 라이브러리
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

# --- LLM 및 프롬프트 초기화 ---
llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)

translation_prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 한국어로 번역하는 번역 전문가야. 다음 내용을 한국어로 번역해줘."),
    MessagesPlaceholder(variable_name="messages"),
])

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", """
당신은 전문적인 요약가입니다. 사용자가 제공하는 전체 텍스트를 아래 형식과 지침에 따라 요약하십시오.

[출력 포맷]
목차
1. ...
2. ...

1. [항목 제목]
· 핵심 요점 1
· 핵심 요점 2

2. [항목 제목]
· 핵심 요점 1
...
    """),
    MessagesPlaceholder(variable_name="messages"),
])

translation_chain = translation_prompt | llm
summary_chain = summary_prompt | llm

# --- Helper Functions ---

def get_script_from_youtube(url: str) -> Tuple[str, str]:
    """유튜브 URL에서 우선순위에 따라 자막 텍스트와 언어 코드를 추출합니다."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if not match:
        raise ValueError("유효한 유튜브 영상 URL이 아닙니다.")
    video_id = match.group(1)
    api = YouTubeTranscriptApi()
    # 오류 수정을 위해 클래스를 인스턴스화한 후 메서드를 호출합니다.
    # 사용자가 제공한 코드 내용을 반영하여 수정합니다.
    transcript_list = api.list(video_id)
    
    language_codes = [t.language_code for t in transcript_list]
    
    found_transcript = None
    try:
        # 수동 자막 우선 탐색
        found_transcript = transcript_list.find_manually_created_transcript(language_codes)
    except NoTranscriptFound:
        # 수동 자막이 없으면 자동 생성 자막 탐색
        try:
            found_transcript = transcript_list.find_generated_transcript(language_codes)
        except NoTranscriptFound:
             # 어떤 자막도 찾지 못한 경우
             raise TranscriptsDisabled(video_id)

    if not found_transcript:
        raise TranscriptsDisabled(video_id)

    transcript_data = found_transcript.fetch()
    detected_language_code = found_transcript.language_code
    
    full_script = " ".join(entry.text for entry in transcript_data).strip()
    return full_script, detected_language_code


# --- Reflex State ---

class YoutubeState(xt.State):
    """웹 앱의 상태와 전체 워크플로우를 관리합니다."""
    youtube_url: str = ""
    original_script: str = ""
    translated_script: str = ""
    total_summary: str = "" # 요약 결과를 저장할 변수 추가
    source_language: str = ""
    
    is_processing: bool = False
    processing_status: str = "" # 현재 처리 단계를 표시할 변수
    error_message: str = ""

    async def process_video(self):
        """URL을 받아 [추출 -> 번역 -> 요약] 워크플로우를 실행합니다."""
        if not self.youtube_url.strip():
            self.error_message = "유튜브 URL을 입력해주세요."
            return

        # --- 초기화 ---
        self.is_processing = True
        self.error_message = ""
        self.original_script = self.translated_script = self.total_summary = ""
        yield

        try:
            # --- 1. 자막 추출 ---
            self.processing_status = "자막 추출 중..."
            yield
            script, lang_code = get_script_from_youtube(self.youtube_url)
            self.original_script = script
            
            language_map = {'en': 'English', 'ja': 'Japanese', 'es': 'Spanish', 'fr': 'French'}
            self.source_language = language_map.get(lang_code, lang_code)

            # --- 2. 번역 (한국어가 아닐 경우) ---
            script_to_summarize = ""
            if lang_code == 'ko':
                self.translated_script = "원문이 한국어이므로 번역을 건너뜁니다."
                script_to_summarize = self.original_script
                yield
            else:
                self.processing_status = "한국어로 번역 중..."
                yield
                request = HumanMessage(content=self.original_script)
                async for chunk in translation_chain.astream({"messages": [request]}):
                    self.translated_script += chunk.content
                    script_to_summarize += chunk.content
                    yield
            
            # --- 3. 요약 ---
            self.processing_status = "내용 요약 중..."
            yield
            request = HumanMessage(content=script_to_summarize)
            async for chunk in summary_chain.astream({"messages": [request]}):
                self.total_summary += chunk.content
                yield

        except Exception as e:
            self.error_message = f"오류 발생: {e}"
        finally:
            self.is_processing = False
            self.processing_status = ""
            yield
