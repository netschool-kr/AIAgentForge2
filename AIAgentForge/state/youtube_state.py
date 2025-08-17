# -*- coding: utf-8 -*-
import os
import re
import reflex as xt
# youtube_transcript_api 임포트 방식을 표준 형태로 수정
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# --- Helper Functions (기존 로직) ---

def get_youtube_script(url: str) -> tuple[str, str]:
    """유튜브 영상 URL에서 자막을 자동으로 감지하고 텍스트를 추출합니다."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if not match:
        raise ValueError("유효한 유튜브 영상 URL이 아닙니다.")
    video_id = match.group(1)

    # 인스턴스 생성 후 새로운 메서드(fetch, list) 사용으로 수정
    api = YouTubeTranscriptApi()
    
    # 사용 가능한 자막 목록을 가져와 언어 코드 확인
    transcript_list = api.list(video_id)
    
    # TranscriptList에서 사용 가능한 language_codes 추출
    language_codes = [t.language_code for t in transcript_list]
    
    detected_language_code = "en" # 기본값 설정
    try:
        # 수동 자막 우선 탐색
        found_transcript = transcript_list.find_manually_created_transcript(language_codes)
        detected_language_code = found_transcript.language_code
    except NoTranscriptFound:
        # 수동 자막이 없으면 자동 생성 자막 탐색
        try:
            found_transcript = transcript_list.find_generated_transcript(language_codes)
            detected_language_code = found_transcript.language_code
        except NoTranscriptFound:
             # 어떤 자막도 찾지 못한 경우, 기본값을 사용
             pass
        else:
            # 자동 생성 자막을 가져옴
            transcript = found_transcript.fetch()
    else:
        # 수동 자막을 가져옴
        transcript = found_transcript.fetch()

    # 만약 자막을 찾지 못했다면, 기본 fetch 시도
    if 'transcript' not in locals():
        transcript = api.fetch(video_id)

    full_script = " ".join(entry.text for entry in transcript).strip()
    return full_script, detected_language_code

# --- Reflex State (애플리케이션의 상태 관리) ---

class YoutubeState(xt.State):
    """웹 앱의 상태와 이벤트 핸들러를 관리합니다."""
    youtube_url: str = ""
    original_script: str = ""
    translated_script: str = ""
    source_language: str = ""
    is_processing: bool = False
    error_message: str = ""

    async def process_video(self):
        """사용자 요청을 받아 자막 추출 및 번역을 수행하는 이벤트 핸들러."""
        if not self.youtube_url.strip():
            self.error_message = "유튜브 URL을 입력해주세요."
            return

        # 이전 상태 초기화 및 처리 시작
        self.is_processing = True
        self.error_message = ""
        self.original_script = ""
        self.translated_script = ""
        self.source_language = ""
        yield

        try:
            # 1. 자막 추출
            script, lang_code = get_youtube_script(self.youtube_url)
            self.original_script = script
            
            language_map = {
                'en': 'English', 'ja': 'Japanese', 'es': 'Spanish', 'fr': 'French',
                'de': 'German', 'ko': 'Korean', 'zh-Hans': 'Simplified Chinese',
            }
            source_language_name = language_map.get(lang_code, lang_code)
            self.source_language = source_language_name
            yield

            # 2. LLM을 이용한 번역 (스트리밍)
            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

            # 시스템 프롬프트를 한국어로 명확하게 변경
            system_prompt = f"당신은 전문 번역가입니다. 다음 '{source_language_name}' 텍스트를 한국어로 번역해주세요."
            translation_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ])
            llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)
            chain = translation_prompt | llm
            
            request_message = HumanMessage(content=self.original_script)
            
            async for chunk in chain.astream({"messages": [request_message]}):
                self.translated_script += chunk.content
                yield

        except (ValueError, NoTranscriptFound, TranscriptsDisabled) as e:
            self.error_message = f"자막 처리 오류: {e}"
        except Exception as e:
            self.error_message = f"알 수 없는 오류가 발생했습니다: {e}"
        finally:
            # 처리 종료
            self.is_processing = False
            yield