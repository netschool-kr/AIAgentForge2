# AIAgentForge2

## Python만으로 나만의 AI Agent 서비스 만들기

이 프로젝트는 **《Python만으로 나만의 AI Agent 서비스 만들기》** 책의 실습 코드 저장소입니다.

**AI 시대, 개발자의 생산성을 극대화하는 새로운 풀스택 아키텍처를 경험하세요.**

### 📚 프로젝트 소개

`AIAgentForge`는 순수 Python과 Reflex 프레임워크를 기반으로 구축된 AI Agent 서비스 플랫폼입니다. 이 프로젝트는 AI 로직과 웹 서비스를 위해 Python과 JavaScript를 오가야 했던 기존의 비효율적인 개발 방식을 극복하고, **‘위대한 백엔드의 재배치(The Great Backend Relocation)’**라는 철학을 실현합니다.

이 저장소의 코드를 통해 다음을 직접 경험하고 학습할 수 있습니다.

- **Reflex**: 순수 Python으로 프론트엔드와 백엔드를 모두 구현하는 통합 개발 경험.
- **Supabase**: 데이터베이스의 RLS(행 수준 보안)를 활용하여 애플리케이션 코드의 보안 로직을 제거하는 방법.
- **비동기 파이프라인**: 외부 의존성 없이 `async/yield`를 통해 장기 실행 작업을 실시간으로 처리하는 기술.
- **고급 검색**: 키워드 검색과 벡터 검색을 융합하는 하이브리드 검색 로직을 PostgreSQL의 RPC로 재배치하는 아키텍처.
- **AI Agent 구현**: 블로그 생성, 유튜브 번역, 심층 리서치 등 다양한 AI 에이전트를 구축하는 실전 노하우.

### 🚀 시작하기

#### 1. 환경 설정

`AIAgentForge`는 Python 3.11 이상을 권장합니다. Conda 환경을 사용하여 프로젝트 의존성을 격리하는 것을 추천합니다.

```bash
conda create -n AIAgentForge python=3.11
conda activate AIAgentForge
pip install -r requirements.txt
