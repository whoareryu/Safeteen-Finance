# CLAUDE.md — Backend (whoareryu)

FastAPI 백엔드 프로젝트 규약. 루트 규칙은 [../CLAUDE.md](../CLAUDE.md)를 먼저 읽는다.

---

## Import 경로 규약

`whoareryu/apps/` 내부에서는 `whoareryu`와 `apps`를 import 루트에서 제거한다.

```python
# ✅
from titanic.adapter.inbound.api...
from gourmet.adapter.inbound.api...

# ❌
from whoareryu.apps.titanic...
from apps.titanic...
```

`core`는 예외 — 반드시 `whoareryu.core.` 접두사를 붙인다.

```python
# ✅
from whoareryu.core.matrix.oracle_database import get_db
```

---

## B1. 실행·경로

| 항목 | 값 |
|------|-----|
| 진입점 | `whoareryu/main.py` → `uvicorn main:app` |
| PYTHONPATH | `whoareryu/`, `whoareryu/apps/` (`main.py`에서 `sys.path` 등록) |
| import 루트 | `titanic.*`, `gourmet.*` · `apps.friday_13th.*` (auth) |
| 환경변수 | `whoareryu/.env` (`DATABASE_URL`, `GEMINI_API_KEY`, Gourmet 외부 API 키 등) |
| DB 모듈 | `core.matrix.oracle_database` (async, Neon) · `core.database`는 re-export |
| Gourmet 동기 DB | `apps.database.get_sync_db` (Gourmet 라우터·레거시 ORM) |

```text
whoareryu/
├── main.py                 # FastAPI 앱, 라우터 마운트
├── core/
│   ├── database.py         # oracle_database shim
│   └── matrix/
│       ├── oracle_database.py   # Base, get_db (async), init_db
│       └── keymaker_api.py      # Gemini 키·클라이언트
├── apps/
│   ├── titanic/            # 헥사고날 참조 구현 (async PG) → _docs/CLAUDE.md 참조
│   ├── gourmet/            # 헥사고날 마이그레이션 완료 (sync PG)
│   ├── gourmet_stub.py     # gourmet import 실패 시 최소 스텁
│   └── friday_13th/        # auth (users)
└── adapters/
    └── db_health_adapter.py
```

`main.py` 라우터:
- `titanic.adapter.inbound.api.titanic_router` → prefix `/titanic`
- `gourmet.adapter.inbound.api.gourmet_router` (실패 시 `gourmet_stub`)

---

## B2. 클린 아키텍처 (헥사고날) — 표준 패턴

**레퍼런스 구현: `apps/titanic`** (feature 단위 슬라이스).  
**적용 대상: `apps/gourmet`** (레이어드 → 동일 패턴으로 이전 완료).  
새 앱 추가 시 이 패턴을 그대로 복제한다.

### B2.1 feature 슬라이스 디렉터리

```text
apps/{app_name}/
├── adapter/
│   ├── inbound/api/
│   │   ├── schemas/{feature}_schema.py    # Pydantic (HTTP 경계)
│   │   └── v1/{feature}_router.py         # FastAPI 라우터
│   └── outbound/
│       ├── orm/{entity}.py                # SQLAlchemy ORM (공유 엔티티)
│       ├── pg/{feature}_pg_repository.py  # DB 구현체
│       └── http/                          # 외부 API (Kakao, OpenWeather 등)
├── app/
│   ├── dtos/{feature}_dto.py              # Command / Query (dataclass)
│   ├── ports/
│   │   ├── input/{feature}_use_case.py    # UseCase ABC
│   │   └── output/{feature}_repository.py # Repository ABC
│   └── use_cases/
│       ├── {feature}_interactor.py        # UseCase 구현 (구 *Service*)
│       └── strategies/                    # 추천 Strategy 패턴
├── dependencies/{feature}.py              # DIP 팩토리 get_{feature}_use_case()
├── _docs/CLAUDE.md                        # 앱별 규약 (시블링 구조)
├── config/                                # .env 외부 API 설정
├── data/                                  # 시드·토픽·CSV ingestion
├── domain/                                # (예약) 순수 엔티티·VO
└── schema/                                # DDL
```

### B2.2 SOLID 원칙

#### SRP — 단일 책임

**한 feature = 한 책임 = 한 슬라이스.** 파일·클래스마다 역할을 하나만 둔다.

| 계층 | 파일·클래스 | 책임 (이것만) |
|------|------------|--------------|
| Inbound | `{feature}_router.py` | HTTP 요청·응답, 스키마 변환 |
| Application | `{feature}_interactor.py` | 유스케이스 오케스트레이션 |
| Port In | `{feature}_use_case.py` | 애플리케이션이 **제공하는** 계약 |
| Port Out | `{feature}_repository.py` | 애플리케이션이 **필요로 하는** 영속성 계약 |
| Outbound | `{feature}_pg_repository.py` | SQL·ORM·커밋 |
| 조립 | `dependencies/{feature}.py` | 구현체 생성·주입만 |

**메서드 이름 정렬:** Input Port ↔ Interactor, Output Port ↔ PgRepository 에서 **동일한 공개 메서드명·시그니처** 유지.

```text
FavoriteUseCase.toggle()        ≡ FavoriteInteractor.toggle()
FavoriteRepository.toggle()     ≡ FavoritePgRepository.toggle()
favorite_router                 → use_case.toggle(...)
```

| 규칙 | 내용 |
|------|------|
| Interactor | Output Port에 **위임**만. `select()`·`db.commit()` 직접 호출 금지 (목표 상태) |
| PgRepository | Port에 선언된 메서드만 구현. HTTP·Pydantic import 금지 |
| Router | 전송 형식 파싱만. 비즈니스 분기·DB 접근 금지 |
| `*_service.py` | 사용 금지 → `{feature}_interactor.py` 단일 |

**명명 규약 (feature=`favorite` 기준):**

```text
FavoriteUseCase          # ports/input/favorite_use_case.py
FavoriteInteractor       # use_cases/favorite_interactor.py
FavoriteRepository       # ports/output/favorite_repository.py
FavoritePgRepository     # adapter/outbound/pg/favorite_pg_repository.py
get_favorite_use_case()  # dependencies/favorite.py
```

#### ISP — 인터페이스 분리

**클라이언트가 쓰지 않는 메서드를 인터페이스에 넣지 않는다.** Python `ABC` + `@abstractmethod`로 포트 정의.

- Input·Output 포트를 **한 파일에 합치지 않음** (feature당 각각 1 ABC).
- 포트 시그니처에는 DTO·도메인 타입을 쓰고, Pydantic 스키마·FastAPI 타입은 **라우터 경계**에만.

```python
class FavoriteUseCase(ABC):
    @abstractmethod
    def toggle(self, db: Session, user: User, command: FavoriteToggleCommand) -> tuple[bool, str]: ...

class FavoriteRepository(ABC):
    @abstractmethod
    def toggle(self, db: Session, *, user_id: int, restaurant_id: int) -> bool: ...
```

#### DIP — 의존성 역전

```text
Router  →  Depends(get_*_use_case)  →  Input Port (UseCase)
Interactor  →  Output Port (Repository)  ←  PgRepository
PgRepository  →  ORM
```

- **라우터**: `Depends(get_{feature}_use_case)` + Input Port 타입만. 구현체 직접 생성 금지.
- **Interactor**: 생성자·필드 타입은 Output Port. 구현체 import는 `dependencies/`에만.
- **조립**: `dependencies/{feature}.py` 한 곳에서 `get_db` / `get_sync_db` + Repository + Interactor 연결.

```python
def get_james_director_use_case(db: AsyncSession = Depends(get_db)) -> JamesDirectorUseCase:
    repository: JamesDirectorRepository = JamesDirectorPgRepository(session=db)
    return JamesDirectorInteractor(repository=repository)
```

#### OCP — 개방-폐쇄

| 확장 지점 | 패턴 | 상태 |
|----------|------|------|
| 추천 알고리즘 | `RecommendationStrategy.recommend()` 구현체 추가 | ✅ 적용 |
| 영속성 교체 | 동일 Output Port의 다른 `*PgRepository` / Mock | ✅ 포트·DIP 준비됨 |
| HTTP 어댑터 | feature별 `*_router.py` 추가 | 🔄 진행 중 |
| 유스케이스 분기 | Interactor 내부 `if/elif` 누적 | ❌ Strategy·Policy로 **추출 예정** |

새 요구사항이 알고리즘·정책 차이면 Interactor를 고치지 말고 **새 Strategy / 새 Port 구현체**를 추가.

#### LSP — 리스코프 치환

| 치환 관계 | 상태 |
|----------|------|
| `{Feature}Interactor` → `{Feature}UseCase` | ✅ Favorite·James |
| `{Feature}PgRepository` → `{Feature}Repository` | ✅ Favorite |
| Mock / InMemory Repository | ❌ 미작성 |
| async ↔ sync Repository | ⚠️ Titanic async / Gourmet sync 통일 전 LSP 위반 가능 |

- Port에서 `@abstractmethod`로 선언한 메서드를 **빠짐없이** 구현. 시그니처 변경 금지.
- `NotImplementedError`·빈 `pass` 스텁은 **배포 경로에 남기지 않음**.

```text
# LSP 검증 질문 (PR 전)
포트 변수에 PgRepository / Mock / 다른 Strategy 를 넣어도
Interactor·Router 가 수정 없이 동작하는가?
```

---

## B2.5 Gourmet — feature Interactor 목록 (22개)

`app/use_cases/*_interactor.py`만 유지 (`*_service.py` 제거 완료).

| feature | 주요 라우터 | 비고 |
|---------|------------|------|
| `favorite` | `favorite_router` | DIP 완료 |
| `meal_plan` | `meal_plan_router` | DIP 완료, Strategy 연동 |
| `restaurant_domain` | `restaurant_router` (v2) | `RestaurantUseCase` |
| `restaurant_detail` | `gourmet_router` | Facade + detail adapter |
| `category_browse` | `gourmet_router` | 넷플릭스형 주제 행 |
| `home_browse` | `gourmet_router` | 홈 피드 |
| `restaurant_search` | `gourmet_router` | 검색 + `search_query` 로그 |
| `daily_pick` | `gourmet_router` | 유저별 1일 1곳 |
| `today_picks` | `gourmet_router` | 날짜별 N선 |
| `category_catalog` | `catalog_router` | food_categories |
| `nearby_restaurants` | `catalog_router` | 거리 기반 |
| `restaurant_menu` | `catalog_router` | |
| `restaurant_enrichment` | `catalog_router` | Kakao + LOCALDATA |
| `search_suggest` | `catalog_router` | |
| `topic_restaurants` | `catalog_router` | |
| `gourmet_chat` | `gourmet_chat_router` | Gemini RAG |
| `restaurant_browse` | (내부) | 여러 interactor가 공유 |
| `restaurant_location` | (내부) | Haversine·좌표 |
| `restaurant_profile` | (내부) | |
| `search_query` | (내부) | |
| `view_stat` | `gourmet_router` | 레거시, 조회 0 고정 |
| `restaurant_coordinates_sync` | (내부) | |

**Strategy** (`app/use_cases/strategies/recommendation_strategy.py`):
- `BudgetBasedRecommendationStrategy` → `meal_plan`
- `CategoryBrowseRecommendationStrategy` → `restaurant_domain`

**라우터 집계**: `gourmet/adapter/inbound/api/__init__.py`  
**DB**: Gourmet ORM은 **sync** `Session` + `get_sync_db`. Titanic은 **async** — 통일은 미완 작업.  
**DDL / ERD**: `apps/gourmet/schema/gourmetmate.sql`

---

## B3. ORM·테이블 규칙

`docs/DevOps/Backend/ENTITY_RULE.md` 필수.

- PK: `id` `int` autoincrement (`IntIdPrimaryKeyMixin`)
- FK: `{entity}_id` → `{table}.id`
- Gourmet 핵심: `restaurants` 허브, 1NF/2NF/3NF 분리 (`restaurant_prices`, `restaurant_contacts`, `restaurant_menus`, …)
- `oracle_database.import_models()`에 등록된 모델만 Alembic/`create_all` 감지

---

## B4. 개발 백로그

### 완료

- [x] Titanic James: 헥사고날 + DIP + 배치 INSERT (타임아웃 해결)
- [x] Gourmet: `app/controllers|services|models|repositories` → adapter/app/dependencies 구조 이전
- [x] Gourmet: `*_service.py` → `*_interactor.py` 단일화
- [x] Gourmet: `favorite`, `meal_plan` DIP 완성 예시
- [x] SOLID: SRP·ISP·DIP(부분), OCP(`RecommendationStrategy`), LSP(Favorite·James)
- [x] Gourmet: `gourmetmate.sql` 프로젝트 정합 DDL 작성

### 진행 중 / 다음 작업

- [ ] **Gourmet** `gourmet_router` / `catalog_router` 엔드포인트를 feature별 `*_router.py`로 분리
- [ ] **Gourmet** 각 `*_pg_repository.py`에 DB 로직 이전 (interactor에서 직접 SQL 제거)
- [ ] **Gourmet** `restaurant_repository.py` → `restaurant_pg_repository.py` 명명 통일
- [ ] **Gourmet** sync → async PG 전환 검토 (Titanic과 DB 레이어 통일)
- [ ] **ORM** `import_models()`에 Gourmet 전 테이블·Titanic ORM 경로 반영
- [ ] **Alembic** 마이그레이션 gourmet 전체 테이블 반영
- [ ] **domain/** (`gourmet/domain/`) 실제 엔티티·VO 채우기 (현재 빈 패키지)
- [ ] **OCP** Interactor 내 `if/elif` 정책 분기 → Strategy·Policy 클래스로 추출
- [ ] **LSP** Repository Mock·InMemory 구현으로 포트 치환 테스트 추가

### 알려진 이슈

| 이슈 | 내용 |
|------|------|
| Gourmet 이중 ORM | `{feature}_orm.py` re-export + 실제 `restaurant.py` 등 공유 — 혼동 주의 |
| `restaurant_view_stats` | ORM 있으나 API는 레거시(항상 0) |
| `main.py` | `titanic.app.james_controller` import는 레거시, 실제 라우팅은 `titanic_router` |
| 순환 import | `titanic.adapter.inbound.api` ↔ ports 로딩 순서 이슈 가능 |

---

## B5. 에이전트 작업 체크리스트

작업 전:
1. `docs/README.md` → 해당 영역 규칙 (`ENTITY_RULE.md`, `EXTERNAL_API_KEYS.md` 등)
2. 대상 앱 (`titanic` / `gourmet`) 하위 CLAUDE.md 확인
3. 기존 feature 슬라이스 패턴 복제 (새 파일보다 James / Favorite 참고)

코딩 시 (SOLID):
- **SRP**: feature 슬라이스 1세트만 추가·수정. UseCase ↔ Interactor, Repository ↔ PgRepository **메서드명 동일**.
- **ISP**: Input/Output Port 분리. 포트에 라우터·ORM이 쓰지 않는 메서드 넣지 않음.
- **DIP**: `dependencies/{feature}.py`에서만 구현체 조립. 라우터·Interactor는 포트 타입만.
- **OCP**: 알고리즘·정책 변경은 Strategy/새 구현체 추가로, 기존 Interactor 최소 수정.
- **LSP**: Port `@abstractmethod` 전부 구현. 시그니처·의미 변경 금지. 스텁 `pass` 배포 금지.
- import: `titanic.*` / `gourmet.*` (`apps.gourmet.app.*` 사용 금지)
- 새 테이블: `IntIdPrimaryKeyMixin` + `ENTITY_RULE.md`
- 범위: 요청과 직접 연결된 파일만 수정
- 새 `.md`: 사용자 승인 없이 생성 금지

검증:
```powershell
cd whoareryu
$env:PYTHONPATH="$PWD;$PWD\apps"
python -c "from gourmet.adapter.inbound.api import gourmet_router; from titanic.adapter.inbound.api import titanic_router; print('ok')"
uvicorn main:app --host 127.0.0.1 --port 8000
```

---

## B6. 외부 연동 (Gourmet)

`docs/DevOps/Backend/EXTERNAL_API_KEYS.md` · `gourmet/config/external_settings.py`

| 클라이언트 | 경로 |
|-----------|------|
| Kakao Local | `adapter/outbound/http/kakao_local_client.py` |
| LOCALDATA | `adapter/outbound/http/localdata_client.py` |
| OpenWeather | `adapter/outbound/http/openweather_client.py` |
| Gemini (채팅) | `core/matrix/keymaker_api.py` + `gourmet_chat_router` |

---

## B7. 참고 문서

| 문서 | 용도 |
|------|------|
| `docs/README.md` | 규칙 인덱스 |
| `docs/DevOps/Backend/ENTITY_RULE.md` | PK·ORM |
| `docs/DevOps/Backend/EXTERNAL_API_KEYS.md` | API 키 |
| `apps/gourmet/schema/gourmetmate.sql` | Gourmet ERD DDL |
| [apps/titanic/_docs/CLAUDE.md](apps/titanic/_docs/CLAUDE.md) | Titanic 앱 규약 |

---

## 관련 문서

[[CLAUDE\|Root]] · [[ENTITY_RULE]] · [[whoareryu/apps/titanic/_docs/CLAUDE\|Titanic CLAUDE]] · [[TITANIC_ERD]] · [[whoareryu/apps/titanic/_docs/titanic_architecture\|titanic_architecture]] · [[whoareryu/apps/titanic/_docs/james_code_review\|james_code_review]] · [[GOURMET_ERD]] · [[gourmetmate_v2_erd]] · [[EXTERNAL_API_KEYS]]
