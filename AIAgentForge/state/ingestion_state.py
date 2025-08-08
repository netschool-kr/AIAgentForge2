# AIAgentForge/state/ingestion_state.py
import reflex as rx
from.base import BaseState
from.collection_state import CollectionState
import asyncio
from reflex.vars import Var
from typing import List, Any # Import Any
import io
import PyPDF2 # PDF 처리를 위한 라이브러리 [9, 10]
import docx # DOCX 처리를 위한 라이브러리 [11, 12]
from langchain.text_splitter import RecursiveCharacterTextSplitter # 텍스트 분할을 위한 LangChain 라이브러리 [13, 14]

class IngestionState(BaseState):
    """파일 업로드 및 수집 파이프라인과 관련된 모든 상태와 로직을 관리합니다."""

    # 여러 파일이 동시에 처리 중인지 여부를 나타내는 플래그
    is_uploading: bool = False

    # 각 파일의 진행률을 추적하는 딕셔너리 (filename: progress)
    upload_progress: dict[str, int] = {}
    
    # 각 파일의 현재 처리 상태를 추적하는 딕셔너리 (filename: status_message)
    upload_status: dict[str, str] = {}

    # 각 파일의 오류 메시지를 저장하는 딕셔너리 (filename: error_message)
    upload_errors: dict[str, str] = {}


    @rx.event(background=True)
    async def handle_upload(self, files: Any):
        """파일 업로드를 처리하고 각 파일에 대한 백그라운드 작업을 시작합니다."""
        collection_id = self.router.page.params["collection_id"]
        async with self:
            self.is_uploading = True
        
        # The 'files' argument will be a list of rx.UploadFile objects at runtime
        for file in files:
            # 각 파일에 대해 별도의 백그라운드 작업을 비동기적으로 시작
            yield IngestionState.process_single_file(file, collection_id)

    @rx.event(background=True)
    async def process_single_file(self, file: rx.UploadFile, collection_id: str):
        """단일 파일을 처리하는 전체 파이프라인."""
        filename = file.filename
        try:
            # 1. 초기 상태 설정
            async with self:
                self.upload_progress[filename] = 0
                self.upload_status[filename] = "업로드 중..."
            
            content_bytes = await file.read()

            # 2. 텍스트 추출
            async with self:
                self.upload_status[filename] = "텍스트 추출 중..."
            
            text = ""
            if "pdf" in file.content_type:
                reader = PyPDF2.PdfReader(io.BytesIO(content_bytes)) # [9, 10]
                for page in reader.pages:
                    text += page.extract_text()
            elif "vnd.openxmlformats-officedocument.wordprocessingml.document" in file.content_type:
                doc = docx.Document(io.BytesIO(content_bytes)) # [11, 12]
                for para in doc.paragraphs:
                    text += para.text + "\n"
            
            async with self:
                self.upload_progress[filename] = 25
                # 3. 텍스트 분할 (Chunking)
                self.upload_status[filename] = "텍스트 분할 중..."
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) # [13, 14]
            chunks = text_splitter.split_text(text)

            async with self:
                self.upload_progress[filename] = 50

                # 4. 임베딩 생성 및 5. 데이터베이스 삽입
                self.upload_status[filename] = "임베딩 생성 및 저장 중..."
            
            # (이 부분은 OpenAI API 호출 및 Supabase DB 삽입 로직으로 채워집니다.)
            # 예: OpenAI 임베딩 API 호출, document_sections 테이블에 배치 삽입
            # 진행률을 50%에서 100%까지 점진적으로 업데이트
            
            # 6. 완료
            async with self:
                self.upload_progress[filename] = 100
                self.upload_status[filename] = "완료"

        except Exception as e:
            async with self:
                self.upload_errors[filename] = f"처리 중 오류 발생: {str(e)}"
                self.upload_status[filename] = "오류"
        
        finally:
            # 모든 파일 처리가 끝났는지 확인 후 is_uploading 상태 해제
            # (이 로직은 handle_upload의 마지막에 추가되어야 합니다)
            pass