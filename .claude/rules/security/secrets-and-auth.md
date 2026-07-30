---
paths:
  - "fastapi/**/*.py"
  - "**/.env*"
  - "docker-compose*.yaml"
---

# 시크릿 · 인증 규칙

이 프로젝트는 결제(PCI)를 다루지 않는다 — 대신 시크릿 관리와 RS256 인증 분리가
실제 보안 경계다.

---

## 1. 시크릿은 `secret_manager` 경유

`os.getenv(...)`를 산재해서 호출하지 않는다. `fastapi/core/matrix/secret_manager.py`의
`secret_manager.get_secret(key, default=...)`를 쓴다.

```python
from core.matrix.secret_manager import secret_manager

api_key = secret_manager.get_secret("GEMINI_API_KEY")           # 없으면 즉시 RuntimeError
base_url = secret_manager.get_secret("OLLAMA_BASE_URL", "http://localhost:11434")  # 폴백
```

- `default`를 안 주면 값이 없을 때 **즉시 실패**한다 (조용히 `None`으로 흘러가지 않는다).
- 코드에 시크릿 문자열을 하드코딩하지 않는다.

---

## 2. `.env*`는 절대 커밋 금지

루트 `.gitignore`가 `.env`, `.env*`를 전부 차단한다. 새 시크릿 키를 추가하면
`fastapi/.env.example` / `www/.env.example`에 **키만**(값은 플레이스홀더로) 같이
추가한다.

---

## 3. RS256 키 분리 — `JWT_PRIVATE_KEY`는 `auth` 서비스에만

`api.whoareryu.cloud`(`fastapi/main.py`)와 `auth.whoareryu.cloud`
(`fastapi/auth_main.py`)는 같은 이미지를 다른 엔트리포인트로 띄운 별도 컨테이너다.

| 키 | 위치 | 용도 |
|----|------|------|
| `JWT_PRIVATE_KEY` | `fastapi/.env.auth` (auth 서비스 전용) | 토큰 서명 |
| `JWT_PUBLIC_KEY` | `fastapi/.env` (backend에서도 읽음) | 토큰 검증만 |

`main.py`(backend) 쪽 코드에 `JWT_PRIVATE_KEY`를 참조하는 코드를 추가하지 않는다
— backend는 공개키 검증만 해야 한다는 게 이 분리의 목적이다.

---

## 4. 로컬(bare) 실행 시 Docker 전용 호스트명 주의

`fastapi/.env`의 `OLLAMA_HOST=http://host.docker.internal:11434`,
`DATABASE_URL=...@pgvector:5432/...`는 **Docker 컨테이너 안에서만** 풀리는
호스트명이다. `.env` 자체를 고치지 말고, 로컬 셸에서 `export`로 override한다
(`OLLAMA_HOST=http://127.0.0.1:11434`, `DATABASE_URL=...@127.0.0.1:5432/...`).
