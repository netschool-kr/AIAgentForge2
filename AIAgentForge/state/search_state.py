
# AIAgentForge/state/search_state.py
import reflex as rx
from.base import BaseState
from openai import AsyncOpenAI

# 환경 변수에서 OpenAI API 키를 가져와 클라이언트를 초기화합니다.
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class SearchState(BaseState):
    search_query: str = ""
    is_loading: bool = False
    search_results: list[dict] = []

    async def handle_search(self):
        if not self.search_query.strip():
            return

        self.is_loading = True
        yield

        try:
            # Step 1: Get query embedding
            # (실제 구현에서는 에러 처리와 함께 OpenAI 클라이언트를 사용합니다)
            response = await client.embeddings.create(
                input=self.search_query,
                model="text-embedding-3-small" # 사용하는 모델에 맞게 수정
            )
            query_embedding = response.data.embedding

            # Step 2: Call the cognitive partner!
            response = await self.supabase_client.rpc(
                "hybrid_search_multilingual",
                params={
                    "query_text": self.search_query,
                    "query_embedding": query_embedding,
                    "match_count": 10  # 상위 10개 결과를 요청
                }
            ).execute()

            self.search_results = response.data

        except Exception as e:
            # (실제 구현에서는 사용자에게 보여줄 에러 상태를 설정합니다)
            print(f"Search failed: {e}")
            self.search_results = []
        finally:
            self.is_loading = False
            yield

