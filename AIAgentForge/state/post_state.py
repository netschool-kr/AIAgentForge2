# AIAgentForge/state/post_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState

class PostState(BaseState):
    """게시판별 게시글 관리(CRUD, 검색)를 위한 상태"""

    # 현재 게시판 정보
    board_id: str = ""
    board_name: str = ""
    board_description: str = ""

    # 게시글 목록
    posts: list[dict] = []

    # UI 상태
    is_loading: bool = False
    search_query: str = ""

    @rx.var
    def board_id_from_router(self) -> str:
        """라우터 경로에서 board_id를 가져옵니다."""
        return self.router.page.params.get("board_id", "")

    async def load_board_and_posts(self):
        """페이지 로드 시 게시판 정보와 게시글 목록을 함께 불러옵니다."""
        self.is_loading = True
        self.board_id = self.board_id_from_router
        yield

        if not self.board_id:
            self.is_loading = False
            print("Board ID not found in URL.")
            yield
            return

        try:
            board_res = self.supabase_client.from_("boards").select("*").eq("id", self.board_id).single().execute()
            self.board_name = board_res.data.get("name", "알 수 없는 게시판")
            self.board_description = board_res.data.get("description", "")

            posts_res = self.supabase_client.from_("posts").select("*").eq("board_id", self.board_id).order("created_at", desc=True).execute()
            self.posts = posts_res.data
        except Exception as e:
            print(f"Error loading board and posts: {e}")
        finally:
            self.is_loading = False
            yield

    async def handle_search(self):
        """현재 게시판 내에서 게시글을 검색합니다."""
        if not self.search_query.strip():
            yield PostState.load_board_and_posts
            return

        self.is_loading = True
        yield
        try:
            response = self.supabase_client.from_("posts").select("*") \
                .eq("board_id", self.board_id) \
                .or_(f"title.ilike.%{self.search_query}%,content.ilike.%{self.search_query}%") \
                .order("created_at", desc=True).execute()
            self.posts = response.data
        except Exception as e:
            print(f"Error searching posts: {e}")
        finally:
            self.is_loading = False
            yield

    async def create_post(self, form_data: dict):
        """새로운 게시글을 생성합니다."""
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.is_authenticated:
                return

            self.supabase_client.from_("posts").insert({
                "title": form_data["title"],
                "content": form_data["content"],
                "board_id": self.board_id,
                "author_email": auth_state.user.email,
            }).execute()

            yield PostState.load_board_and_posts
            yield rx.redirect(f"/boards/{self.board_id}")
        except Exception as e:
            print(f"Error creating post: {e}")

# --- [게시글 상세 페이지를 위한 State] ---
class PostDetailState(BaseState):
    """게시글 상세 보기, 수정, 삭제를 위한 상태"""
    post: dict = {}
    is_loading: bool = False
    is_editing: bool = False # 수정 모드 여부를 제어하는 상태

    @rx.var
    def post_id_from_router(self) -> str:
        """라우터에서 post_id를 가져옵니다."""
        return self.router.page.params.get("post_id", "")

    @rx.var
    def is_author(self) -> bool:
        """현재 로그인한 사용자가 게시글 작성자인지 확인합니다."""
        # [FIXED] get_state()는 비동기 함수이므로 @rx.var 내부에서 직접 사용할 수 없습니다.
        # BaseState에 있는 is_authenticated와 user 상태를 직접 사용하도록 수정합니다.
        if not self.is_authenticated or not self.user or not self.post:
            return False
        return self.user.id == self.post.get("user_id")
    
    @rx.var
    def formatted_created_at(self) -> str:
        """생성 날짜를 보기 좋은 형식으로 변환합니다."""
        if created_at := self.post.get("created_at"):
            return created_at.replace("T", " ")[:16]
        return ""

    def toggle_edit(self):
        """수정 모드를 토글합니다."""
        self.is_editing = not self.is_editing

    async def load_post(self):
        """ID를 기반으로 특정 게시글의 상세 정보를 불러옵니다."""
        self.is_loading = True
        post_id = self.post_id_from_router
        yield

        if not post_id:
            self.is_loading = False
            print("Post ID not found in URL.")
            return

        try:
            response = self.supabase_client.from_("posts").select("*").eq("id", post_id).single().execute()
            self.post = response.data or {}
        except Exception as e:
            print(f"Error loading post detail: {e}")
        finally:
            self.is_loading = False
            yield

    async def update_post(self, form_data: dict):
        """게시글 내용을 수정합니다."""
        if not self.is_author:
            print("Permission denied for update.")
            return

        post_id = self.post.get("id")
        try:
            self.supabase_client.from_("posts").update({
                "title": form_data["title"],
                "content": form_data["content"],
            }).eq("id", post_id).execute()
            
            # 수정 완료 후, 수정 모드를 끄고 데이터를 새로고침합니다.
            self.is_editing = False
            yield PostDetailState.load_post
        except Exception as e:
            print(f"Error updating post: {e}")

    async def delete_post(self):
        """게시글을 삭제하고 게시판 목록 페이지로 리디렉션합니다."""
        if not self.is_author:
            print("Permission denied for deletion.")
            return

        board_id = self.post.get("board_id")
        post_id = self.post.get("id")

        try:
            self.supabase_client.from_("posts").delete().eq("id", post_id).execute()
            if board_id:
                yield rx.redirect(f"/boards/{board_id}")
            else:
                yield rx.redirect("/boards")
        except Exception as e:
            print(f"Error deleting post: {e}")
