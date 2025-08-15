# AIAgentForge

![AIAgentForge Logo](assets/logo.png) <!-- 로고 이미지가 있으면 assets에 추가하고 경로 수정 -->

AIAgentForge는 사용자가 업로드한 문서를 기반으로 AI가 답변을 생성하는 검색 증강 생성(RAG) 플랫폼입니다. 이 프로젝트는 원래 Next.js와 FastAPI로 개발된 ['Langconnect-client'](https://github.com/teddynote-lab/langconnect-client)에 영감을 받아, JavaScript 없이 순수 Python만으로 풀스택 개발이 가능한 Reflex 프레임워크와 Supabase 데이터베이스를 사용해 재구축된 버전입니다.

이 레포지토리는 책 《Reflex와 Supabase로 Python만으로 AI AgentForge 구축하기》의 코드와 예제를 포함합니다. 책의 철학인 '위대한 백엔드의 재배치'를 바탕으로, AI 개발자가 Python 생태계에서 UI, 백엔드, 데이터베이스 로직을 통합적으로 관리할 수 있도록 설계되었습니다.

## 주요 기능

- **컬렉션 관리**: 문서 그룹 생성 및 관리.
- **지능형 수집 파이프라인**: PDF, DOCX 등 다양한 형식의 문서 업로드 시 자동 텍스트 추출, 의미 단위 분할, 벡터 임베딩 변환 및 데이터베이스 저장.
- **하이브리드 검색**: 키워드 기반 검색(Full-Text Search)과 의미 기반 벡터 검색 결합으로 정확한 결과 제공.
- **AI 어시스턴트 통합 (MCP)**: AI 에이전트가 검색 기능을 API로 호출하고 실시간 스트리밍 받을 수 있는 엔드포인트 제공.
- **Reflex 기반 풀스택**: UI, 상태 관리, 백엔드 로직을 Python으로 통합.
- **Supabase 통합**: 인증, 행 수준 보안(RLS), 벡터 데이터베이스 지원.

## 필수 요구사항

- Python 3.11+
- Conda (가상 환경 관리 추천)
- Supabase 계정 (프로젝트 생성 후 URL 및 ANON_KEY 필요)
- Reflex 라이브러리

## 설치 및 설정

1. **레포지토리 클론**:
   ```
   git clone https://github.com/netschool-kr/AIAgentForge.git
   cd AIAgentForge
   ```

2. **Conda 가상 환경 생성 및 활성화**:
   ```
   conda create -n AIAgentForge python=3.11
   conda activate AIAgentForge
   ```

3. **의존성 설치**:
   ```
   pip install -r requirements.txt
   ```

4. **환경 변수 설정**:
   - `.env` 파일을 루트 디렉토리에 생성하고 다음을 추가:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_ANON_KEY=your_supabase_anon_key
     TEST_USER_EMAIL=your_test_email
     TEST_USER_PASSWORD=your_test_password
     ```
   - Supabase 프로젝트에서 데이터베이스 테이블 및 RLS 정책 설정 (책 4~5장 참조).

5. **Reflex 초기화** (이미 설정된 경우 생략):
   ```
   reflex init
   ```

## 실행 방법

1. **개발 서버 실행**:
   ```
   reflex run
   ```
   - GUI: http://localhost:3000
   - API: http://localhost:8000 (예: /api/v1/mcp/stream)

2. **테스트 스크립트 실행**:
   - 토큰 생성: `python scripts/get_token.py`
   - MCP 스트림 테스트: `python scripts/test_mcp_stream.py`

3. **VS Code 디버깅**:
   - `.vscode/launch.json` 설정 후 F5 키로 실행 (책 2장 참조).

## 프로젝트 구조

```
AIAgentForge/
├── .env                  # 환경 변수
├── requirements.txt      # 의존성 목록
├── rxconfig.py           # Reflex 설정
├── assets/               # 정적 파일 (이미지, CSS 등)
└── AIAgentForge/
    ├── __init__.py
    ├── api/              # API 라우터 및 의존성 (FastAPI 통합)
    ├── components/       # 재사용 UI 컴포넌트
    ├── pages/            # 페이지 UI 정의 (e.g., dashboard.py)
    ├── scripts/          # 테스트 스크립트 (e.g., get_token.py)
    ├── state/            # 상태 관리 클래스 (e.g., dashboard_state.py)
    ├── utils/            # 유틸리티 함수 (e.g., embedder.py)
    └── AIAgentForge.py   # 메인 앱 진입점
```

- **state/**: 애플리케이션 상태 (rx.State) 관리.
- **pages/**: UI 컴포넌트 정의.
- **api/**: FastAPI 기반 API 엔드포인트 (MCP 스트리밍 등).

## 사용 예시

- **문서 업로드 및 검색**:
  - GUI에서 컬렉션 생성 후 문서 업로드.
  - 쿼리 입력 시 하이브리드 검색 결과 표시.

- **AI 에이전트 통합**:
  - MCP 엔드포인트 호출: POST /api/v1/mcp/stream (JSON: {"query": "...", "collection_id": "..."})

## 기여

1. 이슈 제출 또는 PR 환영.
2. 코드 스타일: PEP 8 준수.
3. CI/CD: GitHub Actions로 테스트 실행.

## 라이선스

MIT License. 자세한 내용은 [LICENSE](LICENSE) 파일 참조.

## 참고 자료

- 책: 《Reflex와 Supabase로 Python만으로 AI AgentForge 구축하기》 (황삼청, 2025)
- Reflex 공식 문서: [https://reflex.dev/docs](https://reflex.dev/docs)
- Supabase 문서: [https://supabase.com/docs](https://supabase.com/docs)
- 원본 영감: [Langconnect-client](https://github.com/teddynote-lab/langconnect-client)

문의: [netschool-kr](https://github.com/netschool-kr)