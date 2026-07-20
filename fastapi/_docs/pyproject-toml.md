# A2A 멀티 에이전트 프로젝트 — pyproject.toml 하네스 스펙

## 목적

3개 에이전트(온프레미스 EXAONE, 온프레미스 Qwen, AWS 라우터)로 구성된 A2A-over-MCP
포트폴리오 프로젝트의 파이썬 패키징 구조를 생성한다. 패키지 관리자는 `uv`를 사용한다.

---

## 아키텍처 전제

- **온프레미스 로컬 머신 (MacBook Air 15, Apple M5, 통합 메모리 24GB, macOS)**
  - EXAONE 3.5 2.4B, Qwen2.5 3B를 Ollama로 구동 (Apple Silicon GPU — Metal 백엔드)
  - 통합 메모리 24GB 기준: 두 모델 동시 로드 가능 (EXAONE ~1.5GB + Qwen2.5 3B ~2.0GB, 여유 충분)
  - 그래프 DB (Neo4j) 동거 — Docker 컨테이너로 실행
  - Cloudflare Tunnel 또는 Tailscale 경유로 AWS와 통신
  - `ollama serve`는 `http://localhost:11434` 기본 포트 사용
  - 주의: 팬리스 설계이므로 장시간 고부하 추론 시 서멀 스로틀링 가능 — 배치 추론보다 인터랙티브 호출 패턴에 적합

- **AWS (t4g.micro 또는 Lambda)**: LLM 없는 오케스트레이터/라우터 에이전트.
  온프레미스와 Cloudflare Tunnel/Tailscale 경유 통신.

- 각 에이전트는 MCP 서버로 노출되며, 상대 에이전트를 MCP 클라이언트로 호출한다
  (A2A over MCP).

- 그래프 DB는 온프레미스 에이전트만 직접 접근한다. AWS 라우터는 MCP 경유로만 데이터에
  접근한다.

- 결과물은 Vercel 프론트엔드로 전달된다 (온프레미스 FastAPI → Vercel fetch).

---

## 디렉터리 구조 (생성 대상)

```
a2a-mcp/
├── shared/
│   ├── pyproject.toml
│   └── src/
│       └── a2a_shared/
│           ├── __init__.py
│           └── schemas.py          # A2A 메시지 스키마 (pydantic)
├── agents/
│   ├── exaone/
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── agent_exaone/
│   │           └── __init__.py
│   ├── qwen/
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── agent_qwen/
│   │           └── __init__.py
│   └── aws_router/
│       ├── pyproject.toml
│       └── src/
│           └── agent_aws_router/
│               └── __init__.py
└── README.md
```

> **주의:** `uv workspace`를 사용하지 않는다. 배포 대상이 물리적으로 분리되어 있으므로
> (맥북 로컬 서버 vs AWS), 각 에이전트 디렉터리가 독립적인 `uv sync` 단위가 된다.

---

## 파일 1: `shared/pyproject.toml`

```toml
[project]
name = "a2a-shared"
version = "0.1.0"
description = "A2A 메시지 스키마 및 공통 타입 (에이전트 간 단일 소스)"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.7",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/a2a_shared"]
```

---

## 파일 2: `agents/exaone/pyproject.toml`

> Apple M5 Metal 백엔드로 Ollama가 GPU 가속을 자동 활성화한다.
> `ollama pull exaone3.5:2.4b` 로 모델을 내려받은 뒤 사용한다.

```toml
[project]
name = "agent-exaone"
version = "0.1.0"
description = "온프레미스 주 추론 에이전트 (EXAONE 3.5 2.4B via Ollama — Apple M5 Metal)"
requires-python = ">=3.11"
dependencies = [
    "a2a-shared",
    "fastapi>=0.111",
    "uvicorn[standard]>=0.30",
    "httpx>=0.27",
    "ollama>=0.3",
    "neo4j>=5.20",
    "mcp>=1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.5",
    "mypy>=1.10",
]

[tool.uv.sources]
a2a-shared = { path = "../../shared", editable = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/agent_exaone"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
strict = true
```

---

## 파일 3: `agents/qwen/pyproject.toml`

> `agent-exaone`과 동일한 구조. 아래 항목만 다르다.
> `ollama pull qwen2.5:3b` 로 모델을 내려받은 뒤 사용한다.

```toml
[project]
name = "agent-qwen"
version = "0.1.0"
description = "온프레미스 보조 에이전트 (Qwen2.5 3B via Ollama — Apple M5 Metal)"
requires-python = ">=3.11"
dependencies = [
    "a2a-shared",
    "fastapi>=0.111",
    "uvicorn[standard]>=0.30",
    "httpx>=0.27",
    "ollama>=0.3",
    "neo4j>=5.20",
    "mcp>=1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.5",
    "mypy>=1.10",
]

[tool.uv.sources]
a2a-shared = { path = "../../shared", editable = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/agent_qwen"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
strict = true
```

---

## 파일 4: `agents/aws_router/pyproject.toml`

> LLM·GPU·그래프 DB 의존성을 절대 포함하지 않는다 (`ollama`, `neo4j` 금지).
> t4g.micro 메모리와 콜드스타트를 위해 최소 의존성을 유지한다.

```toml
[project]
name = "agent-aws-router"
version = "0.1.0"
description = "AWS 오케스트레이터/라우터 에이전트 (LLM 없음, MCP 경유 위임)"
requires-python = ">=3.11"
dependencies = [
    "a2a-shared",
    "fastapi>=0.111",
    "uvicorn[standard]>=0.30",
    "httpx>=0.27",
    "mcp>=1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.5",
    "mypy>=1.10",
]

[tool.uv.sources]
a2a-shared = { path = "../../shared", editable = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/agent_aws_router"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
strict = true
```

---

## 파일 5: `shared/src/a2a_shared/schemas.py`

```python
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AgentName(StrEnum):
    EXAONE = "exaone"
    QWEN = "qwen"
    AWS_ROUTER = "aws_router"


class A2AMessage(BaseModel):
    """에이전트 간 표준 메시지. 모든 A2A 호출은 이 스키마를 사용한다."""

    sender: AgentName
    receiver: AgentName
    task: str
    payload: dict = Field(default_factory=dict)
    trace_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class A2AResult(BaseModel):
    trace_id: str
    responder: AgentName
    success: bool
    output: dict = Field(default_factory=dict)
    error: str | None = None
```

---

## 실행 지침 (Claude Code용)

### Step 1 — 디렉터리 및 파일 생성

위 디렉터리 구조를 생성한다. 각 `__init__.py`는 빈 파일로 둔다.
파일 1~5를 명시된 경로에 작성한다.

### Step 2 — 각 패키지 `uv sync` 검증

```bash
cd shared && uv sync && cd ..
cd agents/exaone && uv sync && cd ../..
cd agents/qwen && uv sync && cd ../..
cd agents/aws_router && uv sync && cd ../..
```

### Step 3 — 공통 스키마 import 검증

```bash
cd agents/exaone && uv run python -c "from a2a_shared.schemas import A2AMessage; print('ok')"
```

### Step 4 — aws_router 금지 의존성 확인

```bash
cd agents/aws_router && uv pip list | grep -E "ollama|neo4j" \
  && echo "FAIL: 금지 의존성 발견" || echo "ok"
```

### Step 5 — Ollama 모델 확인 (맥북 로컬)

```bash
# Apple M5 Metal 백엔드 자동 사용 — 별도 설정 불필요
ollama list | grep -E "exaone|qwen"
# 없으면:
ollama pull exaone3.5:2.4b
ollama pull qwen2.5:3b
```

---

## 제약 사항

- **Python 버전은 3.11 고정** (`requires-python = ">=3.11"`). 맥북과 AWS 인스턴스 간 버전 일치 확인 필요.
- **`a2a-shared`는 editable 로컬 경로 의존성**이다. 배포 시 각 서버에 `shared/` 디렉터리가 함께 복사되어야 한다 (git clone 단위가 모노레포 전체이므로 충족됨).
- **버전 상한(`<`)은 지정하지 않는다.** 잠금은 `uv.lock`이 담당한다.
- **스키마 변경은 반드시 `shared/`에서만 한다.** 에이전트 개별 디렉터리에 스키마를 복제하지 않는다.
- **온프레미스 = 맥북 로컬.** RTX GPU가 없으므로 CUDA 관련 패키지(`torch`, `bitsandbytes` 등)는 의존성에 포함하지 않는다. Ollama가 Metal 가속을 내부적으로 처리한다.
- **팬리스 주의.** 장시간 연속 추론 시 서멀 스로틀링이 발생할 수 있다. 포트폴리오 데모 목적이므로 짧은 인터랙티브 호출 패턴으로 설계한다.
