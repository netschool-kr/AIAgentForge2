
# AIAgentForge/state/search_state.py
import os
import reflex as rx
from.base import BaseState
from .document_state import DocumentState
from .auth_state import AuthState
from openai import AsyncOpenAI
from ..utils.embedder import generate_embeddings

# 환경 변수에서 OpenAI API 키를 가져와 클라이언트를 초기화합니다.
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class SearchState(BaseState):
    search_query: str = ""
    is_loading: bool = False
    search_results: list[dict] = []

    async def handle_search(self):
        if not self.search_query.strip():
            return
        
        print("handle_search: ", self.search_query)

        self.is_loading = True
        yield

        try:
            # Step 1: Get query embedding

            embeddings_list = await generate_embeddings([self.search_query])
            if not embeddings_list:
                raise ValueError("임베딩 생성에 실패했습니다.")
            query_embedding = embeddings_list[0]

            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                print("사용자를 찾을 수 없습니다.")
                self.alert_message = "사용자를 찾을 수 없습니다."
                self.show_alert = True
                self.is_uploading = False
                return
            user_id = auth_state.user.id

            doc_state = await self.get_state(DocumentState)

            # Step 2: Call the cognitive partner!
            response =  self.supabase_client.rpc(
                "hybrid_search_multilingual_test",
                params={
                    "query_text": self.search_query,
                    "query_embedding": query_embedding,
                    "p_collection_id": doc_state.collection_id,
                    "p_owner_id": user_id,
                    "match_count": 10,  # 상위 10개 결과를 요청
                }
            ).execute()
            self.search_results = response.data

            # import json  # 필요 시
            # with open('query_embedding.txt', 'w') as f:
            #     f.write(str(query_embedding))

        except Exception as e:
            # (실제 구현에서는 사용자에게 보여줄 에러 상태를 설정합니다)
            print(f"Search failed: {e}")
            self.search_results = []
        finally:
            self.is_loading = False
            yield

