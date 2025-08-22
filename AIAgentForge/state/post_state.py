# AIAgentForge/state/post_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState
from typing import Optional
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PostState(BaseState):
    """게시판별 게시글 관리(CRUD, 검색)를 위한 상태"""

    curr_board_id: Optional[str] = None

    # 현재 게시판 정보
    board_name: str = ""
    board_description: str = ""

    # 게시글 목록
    posts: list[dict] = []

    # UI 상태
    is_loading: bool = False
    search_query: str = ""

    async def load_board_and_posts(self):
        """페이지 로드 시 게시판 정보와 게시글 목록을 함께 불러옵니다."""
        logging.info(f"Loading board with ID: {self.curr_board_id}")
        self.is_loading = True
        yield

        if not self.curr_board_id:
            self.is_loading = False
            logging.info("Board ID not found in URL.")
            yield
            return

        try:
            # 게시판 정보 조회
            board_res = self.supabase_client.from_("boards").select("*").eq("id", self.curr_board_id).single().execute()
            self.board_name = board_res.data.get("name", "알 수 없는 게시판")
            self.board_description = board_res.data.get("description", "")

            # 게시글 목록 조회
            posts_res = self.supabase_client.from_("posts").select("*, author_email:users(email)").eq("board_id", self.curr_board_id).order("created_at", desc=True).execute()
            self.posts = posts_res.data
        except Exception as e:
            logging.info(f"Error loading board and posts: {e}")
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
            response = self.supabase_client.from_("posts").select("*, author_email:users(email)") \
                .eq("board_id", self.curr_board_id) \
                .or_(f"title.ilike.%{self.search_query}%,content.ilike.%{self.search_query}%") \
                .order("created_at", desc=True).execute()
            self.posts = response.data
        except Exception as e:
            logging.info(f"Error searching posts: {e}")
        finally:
            self.is_loading = False
            yield

    async def create_post(self, form_data: dict):
        """새로운 게시글을 생성합니다."""
        try:
            if not self.is_authenticated:
                return

            self.supabase_client.from_("posts").insert({
                "title": form_data["title"],
                "content": form_data["content"],
                "board_id": self.curr_board_id,
                "user_id": self.user.get("id"), # user_id를 직접 저장
            }).execute()

            yield PostState.load_board_and_posts
            yield rx.redirect(f"/boards/{self.curr_board_id}")
        except Exception as e:
            print(f"Error creating post: {e}")
            

class PostDetailState(BaseState):
    """게시글 상세 보기, 수정, 삭제를 위한 상태"""
    
    current_post_id: Optional[str] = None
    post: dict = {}
    is_loading: bool = False
    is_editing: bool = False

    # --- [수정된 부분] ---
    @rx.var
    def is_author(self) -> bool:
        """현재 로그인한 사용자가 게시글 작성자인지 확인합니다."""
        # BaseState를 상속받았으므로 AuthState의 속성에 'self'로 직접 접근합니다.
        # self.get_state()는 비동기 함수라 @rx.var 내부에서 사용할 수 없습니다.
        if not self.is_authenticated or not self.user or not self.post:
            return False
        # self.user는 dict 형태이므로 .get()으로 접근합니다.
        return self.user.get("id") == self.post.get("user_id")
    
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
        yield

        if not self.current_post_id:
            self.is_loading = False
            logging.info("Post ID not found in URL.")
            return

        try:
            # users 테이블에서 email 정보를 함께 가져옵니다.
            response = self.supabase_client.from_("posts").select("*, author_email:users(email)").eq("id", self.current_post_id).single().execute()
            self.post = response.data or {}
        except Exception as e:
            logging.info(f"Error loading post detail: {e}")
        finally:
            self.is_loading = False
            yield

    async def update_post(self, form_data: dict):
        """게시글 내용을 수정합니다."""
        if not await self.is_author():
            logging.info("Permission denied for update.")
            return

        try:
            self.supabase_client.from_("posts").update({
                "title": form_data["title"],
                "content": form_data["content"],
            }).eq("id", self.current_post_id).execute()
            
            self.is_editing = False
            yield PostDetailState.load_post
        except Exception as e:
            print(f"Error updating post: {e}")

    async def delete_post(self):
        """게시글을 삭제하고 게시판 목록 페이지로 리디렉션합니다."""
        if not await self.is_author():
            logging.info("Permission denied for deletion.")
            return

        board_id = self.post.get("board_id")

        try:
            self.supabase_client.from_("posts").delete().eq("id", self.current_post_id).execute()
            if board_id:
                yield rx.redirect(f"/boards/{board_id}")
            else:
                yield rx.redirect("/dashboard")
        except Exception as e:
            print(f"Error deleting post: {e}")
