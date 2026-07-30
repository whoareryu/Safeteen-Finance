# CLAUDE.md

LLM 코딩 시 자주 나는 실패를 줄이기 위한 행동 지침.

**트레이드오프:** 속도보다 신중함을 우선한다. 사소한 작업은 맥락에 맞게 완화해도 된다.

---

## Project Mission & Top-Level Rules

**Mission:** Implement Karpathy-style harness engineering — a Personal Knowledge System (PKS) that integrates Wiki + LLM, enabling the agent to reason over structured knowledge rather than raw memory.

**Architecture mandate (non-negotiable):**
- Strict **SOLID** principles on every class, method, and interface boundary.
- **Hexagonal (Ports & Adapters) + Clean Architecture + DDD** — domain logic never depends on infrastructure; all cross-boundary communication goes through explicit ports.

Violating any of the rules above (SOLID, architecture layers) is a blocker — stop and surface the conflict before writing code.

---

## 하네스가 막는 실패

- **침묵 가정:** 스펙을 추측으로 채우지 않는다.
- **범위 팽창:** "겸사겸사" 리팩터·기능 추가를 하지 않는다.
- **검증 공백:** "돌아가는 것 같다"로 끝내지 않는다.

---

## 1. 구현 전 사고 (Think Before Coding)

**가정하지 않는다. 모호함을 덮지 않고, 트레이드오프는 말로 명확히 한다.**

- 가정은 항상 말로 밝힌다. 불확실하면 질문한다.
- 해석이 여러 갈래면 임의로 하나를 고르지 말고 대안을 나열한다.
- 더 단순한 해법이 있으면 제안한다. 이유가 있으면 정중히 반대해도 된다.
- 불분명하면 멈춘다. 헷갈리는 지점을 구체적으로 짚고 질문한다.

---

## 2. 단순성 우선 (Simplicity First)

**문제를 푸는 데 필요한 최소한의 코드만 쓴다. 추측으로 코드를 넓히지 않는다.**

- 요청받지 않은 기능은 넣지 않는다.
- 일회성 문제를 위해 추상화 층을 새로 만들지 않는다.
- 요청받지 않은 유연성·설정 가능성을 미리 설계하지 않는다.
- 일어날 수 없는 상황을 가정한 방어 코드·예외 처리를 쌓지 않는다.
- 같은 일을 200줄이 아니라 50줄로 쓸 수 있으면, 그렇게 다시 쓴다.

스스로 물어본다: "시니어 엔지니어가 이건 과하게 복잡하다고 할까?" 예라면 단순화한다.

---

## 3. 정밀한 수정 (Surgical Changes)

**꼭 필요한 곳만 고친다. 정리는 자기가 만든 혼란 위주로 한다.**

기존 코드를 고칠 때:
- 옆줄의 코드·주석·포맷을 "개선"한다고 손대지 않는다.
- 망가지지 않은 부분을 리팩터링하지 않는다.
- 내 스타일이 아니어도 기존 스타일을 따른다.
- 작업과 무관한 데드 코드를 보았으면 알려만 주고, 임의로 지우지 않는다.

내 수정 때문에 더 이상 쓰이지 않게 된 것만:
- 불필요해진 import·변수·함수는 제거한다.
- 원래부터 있던 데드 코드는 요청이 없으면 그대로 둔다.

변경 라인 테스트: 바뀐 줄마다 사용자 요청과 직접 연결될 수 있어야 한다.

---

## 4. 목표 중심 실행 (Goal-Driven Execution)

**성공 조건을 정하고, 검증될 때까지 돌린다.**

모호한 일을 검증 가능한 목표로 바꾼다:
- "유효성 검사 추가" → 잘못된 입력에 대한 테스트를 쓰고 통과시킨다.
- "버그 수정" → 버그를 재현하는 테스트를 쓰고, 고친 뒤 통과시킨다.
- "X 리팩터링" → 리팩터링 전후 테스트가 모두 통과한다.

여러 단계일 때는 짧은 계획과 검증 지점을 같이 적는다:
```
1. [단계] → 검증: [무엇으로 확인하는지]
2. [단계] → 검증: [무엇으로 확인하는지]
3. [단계] → 검증: [무엇으로 확인하는지]
```

성공 기준이 분명해야 다음 사람·다음 턴에도 같은 일을 독립적으로 이어갈 수 있다.

---

## 자가 점검

- 이번 변경이 **요청 범위 안**인가?
- **가정·트레이드오프**를 사용자에게 남겼는가?
- **검증**을 실행했거나, 불가능하면 그 이유를 분명히 했는가?

---

## 문서 위치 규칙 (Docs Placement)

새 `.md` 문서를 작성할 때 아래 규칙을 따른다.

| 내용 범위 | 저장 경로 |
|-----------|-----------|
| 프로젝트 전체에 해당하는 공통 문서 | `_docs/` |
| 백엔드(FastAPI + 헥사고날) 전용 문서 | `fastapi/_docs/` |
| 프론트엔드(Next.js + React) 전용 문서 | `www/_docs/` |
| 모바일(Flutter) 전용 문서 | `flutter/_docs/` |

- 범위가 모호할 때는 더 좁은 폴더를 선택한다. 여러 영역에 걸치면 `_docs/`에 둔다.
- 각 `_docs/` 폴더에는 해당 영역의 아키텍처 결정 기록(ADR), 설계 노트, 가이드, 용어 정의 등을 넣는다.
- CLAUDE.md 파일 자체는 이 규칙의 대상이 아니다 (코드베이스 루트 및 각 영역 루트에 위치).

---

## 하위 CLAUDE.md

작업 영역에 맞는 하위 문서를 먼저 읽는다.

| 영역 | 문서 |
|------|------|
| 백엔드 (FastAPI + 헥사고날) | [fastapi/CLAUDE.md](fastapi/CLAUDE.md) |
| 프론트엔드 (Next.js + React) | [www/CLAUDE.md](www/CLAUDE.md) |
| 모바일 (Flutter) | [flutter/CLAUDE.md](flutter/CLAUDE.md) |


---

## 저장소 구조

```text
cloud.whoareryu/
├── fastapi/        # FastAPI 백엔드 (Python, 헥사고날)
├── www/            # Next.js 프론트엔드 (TypeScript)
├── flutter/        # Flutter 모바일 앱
├── a2a-mcp/        # Agent-to-Agent / MCP 실험 코드 (agents/, shared/)
├── training/       # QLoRA 등 로컬 모델 학습 코드 (venv·데이터·산출물은 미추적)
├── _docs/          # 공통 문서 (architecture.md 등)
├── docker-compose.yaml            # 단일 백엔드 스택 (backend·pgvector·redis·cloudflared·adminer)
├── docker-compose.backend.yaml    # 프로덕션 전체 스택 (+auth·n8n·neo4j) — start.sh가 이걸 씀
└── start.sh / stop.sh / start-tunnel.sh
```

`models/`, `ollama-models/`는 수 GB급 모델 바이너리·심볼릭 링크라 `.gitignore` 대상이다 (로컬 전용, 미추적).

---

## 배포

- 프론트엔드(`www/`)는 **Vercel**에 배포된다 (`whoareryu.cloud`, `www.whoareryu.cloud` → Vercel CNAME).
- 백엔드는 Docker 호스트에서 `docker-compose.backend.yaml`로 기동되고, **Cloudflare Tunnel**(named tunnel `whoareryu.cloud`)로 외부에 노출된다. 터널도 `cloudflared` 서비스로 같은 compose 스택 안에서 돈다 (`CLOUDFLARE_TUNNEL_TOKEN` 사용).
- 서브도메인 라우팅(Cloudflare DNS → Tunnel):

  | 서브도메인 | 대상 |
  |-----------|------|
  | `api.whoareryu.cloud` | `backend` 서비스 (`fastapi/main.py`, 8000) |
  | `auth.whoareryu.cloud` | `auth` 서비스 (`fastapi/auth_main.py`, 9000 — 같은 이미지, 다른 엔트리포인트) |
  | `n8n.whoareryu.cloud` | `n8n` 서비스 |
  | `whoareryu.cloud` / `www.whoareryu.cloud` | Vercel |

- `auth`는 `backend`와 완전히 분리된 컨테이너다. RS256 개인키(`JWT_PRIVATE_KEY`)는 `fastapi/.env.auth`에만 있고, `backend`는 공개키로만 토큰을 검증한다.
- 배포 절차: `./start.sh` → `docker compose --env-file fastapi/.env -f docker-compose.backend.yaml pull && up -d` → 안 쓰는 이미지 정리 → `start-tunnel.sh`(Gmail 웹훅 전용 별도 quick tunnel — 메인 API 터널과 무관).
- 로컬에서 컨테이너 없이(bare) 백엔드를 띄울 땐, 컨테이너 안에서만 풀리는 호스트명(`pgvector`, `host.docker.internal`)이 그대로 안 풀린다 — `DATABASE_URL`/`OLLAMA_HOST`를 셸에서 `export`로 `127.0.0.1` 기준 값으로 덮어써야 한다.

---

## 환경 변수

`.env*`는 전부 커밋 금지다 (`.gitignore`가 차단). 예시 파일을 복사해 실제 값을 채운다.

| 파일 | 예시 파일 | 용도 |
|------|-----------|------|
| `fastapi/.env` | `fastapi/.env.example` | 백엔드 전체 설정 (`DATABASE_URL`, `GEMINI_API_KEY`, `OLLAMA_HOST`, OAuth 등) |
| `fastapi/.env.auth` | — | `auth` 서비스 전용 (`JWT_PRIVATE_KEY`) |
| `www/.env.local` | `www/.env.example` | `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_AUTH_URL` |
| 루트 `.env` | — | `docker-compose*.yaml`의 `${VAR}` 치환용 (`CLOUDFLARE_TUNNEL_TOKEN`, `PGVECTOR_*` 등) |

`www/.env.local`에 `NEXT_PUBLIC_BACKEND_URL`/`NEXT_PUBLIC_AUTH_URL`을 안 채우면 로컬 개발 서버가 조용히 프로덕션 도메인으로 요청을 보낸다 — 로컬 백엔드를 테스트할 땐 반드시 채운다.

---

## 테스트

| 도메인 | 프레임워크 | 위치/설정 |
|--------|-----------|-----------|
| fastapi | pytest (`asyncio_mode = auto`) | `fastapi/pytest.ini`, `testpaths = apps` — 앱별 `apps/<앱명>/tests/` |
| flutter | `flutter test` | `flutter/test/` |
| www | 없음 | 검증 수단은 `pnpm build` (ESLint 설정 부재로 `pnpm lint` 미동작) |

`ollama` 마커가 붙은 fastapi 테스트는 로컬 Ollama 서버가 필요하다.

---

## 브랜치 전략

- `main`: 통합 브랜치.
- `mac` / `window`: 작업 PC별 동기화 브랜치.
- 그 외 기능 브랜치(`plant-manager` 등)는 필요할 때 만든다.

---

## 코딩 컨벤션 (공통)

- 커밋 메시지는 **Conventional Commits + 스코프** 형식을 쓴다: `type(scope): 한국어 설명`
  (예: `feat(admin): PDF 업로드→텍스트 추출→요약 파이프라인 추가`, `fix(www): ...`). 여러 도메인에 걸치면 `type(fastapi,www): ...`처럼 콤마로 묶는다.
- 문서·주석·커밋 메시지·사용자 노출 에러 메시지는 한국어로 쓴다.
- `fastapi` / `www` / `flutter`는 서로 직접 임포트하지 않는다. 통신은 HTTP API로만 한다.
- 비밀값은 코드에 하드코딩하지 않고 환경 변수로 주입한다.

---

## 그래프 링크

[[fastapi/CLAUDE\|Backend]] · [[www/CLAUDE\|Frontend]] · [[flutter/CLAUDE\|Flutter]] · [[_docs/architecture\|Master Architecture]]
