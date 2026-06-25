# CLAUDE.md — Backend (whoareryu)

FastAPI 백엔드 프로젝트 규약. 루트 규칙은 [../CLAUDE.md](../CLAUDE.md)를 먼저 읽는다.

---

## 실행·경로

| 항목 | 값 |
|------|-----|
| 진입점 | `whoareryu/main.py` → `uvicorn main:app` |
| PYTHONPATH | `whoareryu/`, `whoareryu/apps/` (`main.py`에서 `sys.path` 등록) |
| 환경변수 | `whoareryu/.env` (`DATABASE_URL`, `GEMINI_API_KEY` 등) |
| DB 모듈 | `core.matrix.gird_oracle_database_manager` (async, Neon PostgreSQL) |
| DB re-export | `core.database`, `apps.database` (동일 심볼 재익스포트) |
| Docker | `docker-compose.yaml` — `app-network` 브리지, backend:8000 |

```text
whoareryu/
├── main.py                        # FastAPI 앱, 라우터 마운트
├── core/
│   ├── database.py                # gird_oracle_database_manager re-export
│   └── matrix/
│       ├── gird_oracle_database_manager.py   # Base, get_db (async), init_db
│       └── ...
├── apps/
│   ├── database.py                # core re-export + get_sync_database_url
│   ├── auth/                      # 인증·사용자 (users 테이블)
│   │   ├── user_model.py          # User ORM
│   │   ├── user_role.py           # UserRole enum (admin/user/partner)
│   │   ├── auth_router.py         # _require_admin()
│   │   └── dependencies.py        # get_current_user() — X-User-Id 헤더
│   ├── titanic/                   # 헥사고날 참조 구현 (async PG)
│   ├── restaurant/                # 맛집 도메인 (sync PG, 22개 feature)
│   ├── user/                      # 즐겨찾기·식비계획
│   └── gourmet_stub.py            # restaurant import 실패 시 최소 스텁
├── alembic/                       # DB 마이그레이션
└── scripts/                       # 운영 유틸 (set_user_role 등)
```

---

## Import 경로 규약

`sys.path`에 `whoareryu/`와 `whoareryu/apps/`가 모두 등록된다.

```python
# ✅ 올바른 예
from titanic.adapter.inbound.api...
from restaurant.adapter.inbound.api...
from user.adapter.inbound.api...
from apps.auth.user_model import User
from apps.database import get_sync_db, Base

# ❌ 금지
from whoareryu.apps.titanic...
from apps.titanic...                 # apps.auth 외 apps.* prefix 금지
from apps.friday_13th...             # 삭제된 모듈
```

`core`는 반드시 전체 경로:
```python
from core.matrix.gird_oracle_database_manager import Base, get_db
from core.database import Base   # 위와 동일 (re-export)
```

---

## 헥사고날 아키텍처 — feature 슬라이스

**레퍼런스 구현: `apps/titanic`** · **적용 완료: `apps/restaurant`**, **`apps/user`**

```text
apps/{app}/
├── adapter/
│   ├── inbound/api/
│   │   ├── schemas/{feature}_schema.py    # Pydantic (HTTP 경계)
│   │   └── v1/{feature}_router.py
│   └── outbound/
│       ├── orm/{entity}_orm.py            # SQLAlchemy ORM
│       └── pg/{feature}_pg_repository.py
├── app/
│   ├── dtos/{feature}_dto.py
│   ├── ports/
│   │   ├── input/{feature}_use_case.py   # ABC
│   │   └── output/{feature}_repository.py # ABC
│   └── use_cases/{feature}_interactor.py
└── dependencies/{feature}_provider.py    # get_{feature}_use_case()
```

### 명명 규칙

```text
FavoriteUseCase          ← ports/input/favorite_use_case.py
FavoriteInteractor       ← use_cases/favorite_interactor.py
FavoriteRepository       ← ports/output/favorite_repository.py
FavoritePgRepository     ← adapter/outbound/pg/favorite_pg_repository.py
get_favorite_use_case()  ← dependencies/favorite_provider.py   ← 반드시 이 이름
```

> `get_{feature}_service` / `get_{feature}_use_case` 혼용 금지 — **반드시 `get_{feature}_use_case`**.

### SOLID 핵심 규칙

| 원칙 | 규칙 |
|------|------|
| SRP | feature 슬라이스 1세트 = 책임 1개. 파일마다 역할 하나. |
| ISP | Input/Output Port 파일 분리. 포트에 라우터·ORM 타입 금지. |
| DIP | `Depends(get_{feature}_use_case)` 만. 라우터·Interactor에서 구현체 직접 import 금지. |
| OCP | 알고리즘 변경 → Strategy 추가. 기존 Interactor 최소 수정. |
| LSP | `@abstractmethod` 전부 구현. 시그니처 변경 금지. `pass` 스텁 배포 금지. |

---

## apps/restaurant — 라우터 목록

`restaurant/adapter/inbound/api/__init__.py`에서 집계.

| 라우터 | prefix | 비고 |
|--------|--------|------|
| `admin_router` | `/gourmet/admin` | `_require_admin` 필요 |
| `gourmet_router` | `/gourmet` | 레거시 통합 (홈·검색·상세) |
| `restaurant_router` | `/gourmet/restaurants` | v2 도메인 |
| `catalog_router` | `/gourmet/catalog` | |
| `category_browse_router` | `/gourmet/categories` | |
| `home_browse_router` | `/gourmet/home` | |
| `restaurant_search_router` | `/gourmet/search` | |
| `daily_pick_router` | `/gourmet/daily-pick` | |
| `today_picks_router` | `/gourmet/today-picks` | |
| `nearby_restaurants_router` | `/gourmet/nearby` | |
| `weather_router` | `/weather` | OpenWeather |
| `gourmet_chat_router` | `/gourmet/chat` | Gemini RAG |

**restaurant ORM FK 규칙:** `ForeignKey("restaurants.id")` — `restaurant` (단수) 금지.

---

## apps/titanic — 라우터 목록

`titanic/adapter/inbound/api/__init__.py`에서 집계, prefix `/api`.

| 라우터 | 캐릭터 | 역할 |
|--------|--------|------|
| `crew_james_director_router` | James | CSV 업로드·배치 INSERT |
| `crew_andrews_architect_router` | Andrews | 통계 분석 |
| `crew_walter_roaster_router` | Walter | 생존 예측 |
| `crew_hartley_violin_router` | Hartley | ML 피처 |
| `crew_lowe_boat_router` | Lowe | `/myself` 엔드포인트 |
| `crew_smith_captain_router` | Smith | 선장 통계 |
| `passenger_*_router` | 6명 | 개별 승객 분석 |

---

## ORM·테이블 규칙

- PK: `IntIdPrimaryKeyMixin` (`id` int autoincrement)
- FK: `ForeignKey("{table_plural}.id")` — **복수형 테이블명** 필수
- users 테이블: `apps/auth/user_model.py` (`role`: admin/user/partner)
- restaurants 허브: `restaurant_prices`, `restaurant_contacts`, `restaurant_menus`, `restaurant_tags`, `restaurant_operating_hours` (1:1 or 1:N)
- Alembic 마이그레이션: `whoareryu/alembic/versions/`

---

## 인증 (apps/auth)

```python
from apps.auth.user_model import User
from apps.auth.user_role import UserRole
from apps.auth.auth_router import _require_admin   # admin 전용 엔드포인트
from apps.auth.dependencies import get_current_user  # X-User-Id 헤더 → User
```

`get_current_user`는 `X-User-Id` (int) 헤더를 읽어 `User` 객체를 반환한다.

---

## 검증

```powershell
cd whoareryu
$env:PYTHONPATH = "$PWD;$PWD\apps"
python -c "from restaurant.adapter.inbound.api import restaurant_router; from titanic.adapter.inbound.api import titanic_router; print('ok')"
```

---

## 알려진 이슈 / 백로그

| 항목 | 상태 |
|------|------|
| restaurant ORM — sync vs titanic async | 통일 미완 |
| `gird_oracle_database_manager` `import_models()` — restaurant ORM 미등록 | Alembic 감지 누락 |
| `get_current_user` — JWT 미구현, X-User-Id 헤더 임시 사용 | 운영 전 교체 필요 |
| `google.generativeai` → `google.genai` 마이그레이션 필요 | FutureWarning 발생 중 |

---

## 머신러닝 데이터 분석 원칙

### Categorical

데이터가 카테고리로 묶일 때 사용한다.

**nominal** : 이름을 바탕으로 하는 척도
순서와는 상관없이 그냥 셀 수 있는 정도의 데이터
ex) 청팀, 홍팀, 백팀

**ordinal** : 순서를 바탕으로 하는 척도
자료들 사이에 순서(서열)가 있는 경우
ex) 청팀이 이길 가능성 1. 매우 낮음 2. 낮음 3. 보통 4. 높음 5. 매우높음

### Quantitative

숫자로 셀 수 있을 때 사용한다.

**interval** : 간격을 바탕으로 하는 척도
기준이 없이 일정한 측정 구간을 갖는 데이터
ex) 11:00~11:05, 온도, pH (10배 덥다·시다 표현 불가)

**ratio** : 비율을 바탕으로 하는 척도
임의의 원점을 기준으로 두고 정하는 데이터
ex) 나이, 돈, 몸무게 (10배 많다·무겁다 표현 가능)

---

## async def vs def 결정 규칙

메소드에 `async`를 붙일지 말지는 **I/O 여부**로만 판단한다.

| 성격 | 예시 | 형태 |
|------|------|------|
| I/O-bound (DB, 네트워크, LLM) | `introduce_myself` | `async def` |
| CPU-bound (형태소 분석, 계산) | `analyze_intent` (Kiwi) | `def` |

**`async def`로 바꿔도 CPU 작업은 비블로킹이 되지 않는다.** 코루틴이 될 뿐이며, Kiwi처럼 오래 걸리는 CPU 연산은 이벤트 루프를 그대로 막는다. `async` 표시가 붙어 있어서 비블로킹인 것처럼 보이지만 실제로는 블로킹 — 더 나쁜 상황이다.

CPU 작업이 실제로 이벤트 루프를 블로킹할 만큼 무거워진 경우, `async def`로 바꾸는 게 아니라 호출 측에서 스레드풀로 넘긴다:

```python
result = await asyncio.to_thread(use_case.analyze_intent, question)
```

---

## 스타 토폴로지 (Star Topology)

**허브:** `apps/star_craft` — 지식 그래프의 중앙 교차점. 온톨로지 상위 개념, 컨텍스트 라우팅, 전역 인덱스 관리.

**스포크:** `apps/silicon_valley`, `apps/titanic`, `apps/restaurant`, `apps/user`, `apps/auth`

### 의존성 방향 규칙 (비선형, 비협상)

```
         [star_craft] ← Hub
        /      |      \
 [titanic] [restaurant] [silicon_valley] ← Spokes
               |
            [user]
```

| 방향 | 허용 여부 | 이유 |
|------|-----------|------|
| Spoke → Hub (`star_craft`) | ✅ 허용 | 허브 포트/인터페이스 사용 |
| Hub → Spoke (직접 import) | ❌ 금지 | Hub는 포트만 정의; 조합은 `main.py`에서만 |
| Spoke → Spoke (직접 import) | ❌ **엄격 금지** | 순환 참조·결합도 발생 원천 |
| 모든 모듈 → `core` | ✅ 허용 | 인프라 공통 레이어 |

**위반 발견 즉시 멈추고 리팩터링 후 진행.** `star_craft`를 거치지 않는 스포크 간 직접 참조는 아키텍처 위반으로 처리한다.

### 하네스 엔지니어링 도구

| 도구 | 파일 | 역할 |
|------|------|------|
| Markdown 린터 | `.markdownlint.yaml` | MD 온톨로지 노드 구조 검증 |
| Import 린터 | `.importlinter` | 스포크→스포크 직접 import 정적 차단 |
| 토폴로지 검증기 | `scripts/validate_harness.py` | MD 링크 기반 토폴로지 위반 탐지 |

```bash
# 하네스 전체 검증
python scripts/validate_harness.py
lint-imports --config .importlinter
markdownlint --config .markdownlint.yaml "**/*.md"
```

---

## 관련 문서

[[fastapi/_docs/entity-rules\|엔티티 규칙]] · [[fastapi/_docs/auth-rules\|인증 규칙]] · [[fastapi/_docs/db-rules\|DB 규칙]] · [[fastapi/_docs/scaffold-rules\|스캐폴드 규칙]] · [[fastapi/apps/restaurant/_docs/CLAUDE\|Restaurant CLAUDE]] · [[fastapi/apps/titanic/_docs/CLAUDE\|Titanic CLAUDE]]
