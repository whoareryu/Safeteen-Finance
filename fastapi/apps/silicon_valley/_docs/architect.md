# silicon_valley — Architecture Rules

헥사고날(Ports & Adapters) + Clean Architecture 기반. 각 캐릭터(도메인 행위자)가 하나의 수직 슬라이스를 형성한다.

---

## 폴더 구조

```
silicon_valley/
├── adapter/
│   ├── inbound/
│   │   └── api/
│   │       ├── schemas/          # HTTP 요청/응답 모델 (Pydantic BaseModel)
│   │       └── v1/               # FastAPI Router
│   └── outbound/
│       ├── mappers/              # ORM ↔ Domain 변환
│       ├── orm/                  # SQLAlchemy ORM 모델
│       └── repositories/        # Output Port 구현체
├── app/
│   ├── dtos/                     # 레이어 간 데이터 전달 객체 (frozen dataclass)
│   ├── ports/
│   │   ├── input/                # Inbound 포트 (ABC UseCase)
│   │   └── output/               # Outbound 포트 (ABC Port)
│   └── use_cases/                # Interactor (UseCase 구현체)
├── dependencies/                 # DI 팩토리 (FastAPI Depends 조립)
├── domain/
│   ├── constants/
│   ├── entities/
│   └── value_objects/
└── _docs/                        # 아키텍처 문서
```

---

## 파일 네이밍 규칙

모든 파일은 `piper_{character}_{role}_{artifact}.py` 패턴을 따른다.

| 아티팩트 | 접미사 | 예시 |
|---|---|---|
| Inbound Schema | `_schema.py` | `piper_hendricks_ceo_schema.py` |
| Router | `_router.py` | `piper_hendricks_ceo_router.py` |
| DTO | `_dto.py` | `piper_hendricks_ceo_dto.py` |
| Input Port (UseCase) | `_use_case.py` | `piper_hendricks_ceo_use_case.py` |
| Output Port | `_port.py` | `piper_hendricks_ceo_port.py` |
| Interactor | `_interactor.py` | `piper_hendricks_ceo_interactor.py` |
| Repository | `_repository.py` | `piper_hendricks_ceo_repository.py` |
| ORM | `_orm.py` | `piper_hendricks_ceo_orm.py` |
| Mapper | `_mapper.py` | `piper_hendricks_ceo_mapper.py` |
| DI Provider | `_provider.py` | `piper_hendricks_ceo_provider.py` |

---

## 클래스 네이밍 규칙

`{Character}{Role}{Artifact}` 형식. `Piper` 접두사는 클래스에 붙이지 않는다.

| 아티팩트 | 접미사 | 예시 |
|---|---|---|
| Schema | `Schema` | `HendricksCeoSchema` |
| Query DTO | `Query` | `HendricksCeoQuery` |
| Response DTO | `Response` | `HendricksCeoResponse` |
| Input Port | `UseCase` | `HendricksCeoUseCase` |
| Output Port | `Port` | `HendricksCeoPort` |
| Interactor | `Interactor` | `HendricksCeoInteractor` |
| Repository | `Repository` | `HendricksCeoRepository` |
| ORM | `ORM` | `HendricksCeoORM` |
| Mapper | `Mapper` | `HendricksCeoMapper` |

---

## 레이어 의존성 규칙

```
Router → UseCase(Port) → Interactor → OutputPort → Repository
```

- **Router**는 `UseCase` 추상(ABC)만 알고, 구현체(`Interactor`)를 직접 참조하지 않는다.
- **Interactor**는 `OutputPort` 추상(ABC)만 알고, `Repository`를 직접 참조하지 않는다.
- **Domain**(`entities`, `value_objects`, `constants`)은 어떤 레이어도 import하지 않는다.
- **DTO**는 app 레이어 전용. Schema(inbound)와 ORM(outbound)이 DTO로 변환되어 경계를 넘는다.
- **DI 조립**은 `dependencies/` 에서만 한다. Router와 Interactor는 서로를 모른다.

---

## 각 아티팩트의 책임

### `schemas/` — Inbound Schema
- Pydantic `BaseModel` 사용.
- HTTP 계층의 입력 유효성 검사 전용.
- `model_config`에 `json_schema_extra.example` 포함.

### `v1/` — Router
- FastAPI `APIRouter` 사용.
- `Depends`로 UseCase 주입. 구현체 import 금지.
- 리턴 타입은 DTO(`Response`)로 선언.

### `app/dtos/` — DTO
- `@dataclass(frozen=True)` 사용 (불변).
- Query / Response 두 클래스를 같은 파일에 정의.
- 어떤 외부 라이브러리도 import하지 않는다.

### `app/ports/input/` — Input Port (UseCase)
- `ABC` + `@abstractmethod`.
- Router가 의존하는 계약. 메서드 시그니처 = DTO 기반.

### `app/ports/output/` — Output Port
- `ABC` + `@abstractmethod`.
- Interactor가 의존하는 계약. Repository가 구현.

### `app/use_cases/` — Interactor
- `UseCase`를 상속하여 구현.
- 생성자에서 `OutputPort`를 주입받는다.
- 도메인 로직을 담당. ORM·Session·HTTP 관련 코드 금지.

### `adapter/outbound/repositories/` — Repository
- `OutputPort`를 상속하여 구현.
- `AsyncSession`을 생성자 주입. SQLAlchemy 비동기 쿼리 담당.

### `adapter/outbound/orm/` — ORM
- SQLAlchemy `Base` 상속.
- 테이블 미확정 시 `__abstract__ = True` 유지.

### `adapter/outbound/mappers/` — Mapper
- ORM 엔티티 ↔ Domain/DTO 변환 전담.
- ORM 스키마 확정 전까지는 클래스 선언만 유지 (`to_entity` / `to_orm` 미구현 상태 허용).

### `dependencies/` — DI Provider
- FastAPI `Depends` 체이닝으로 의존성 그래프 조립.
- `get_{character}_repository` → `get_{character}_use_case` 두 함수 패턴.
- 리턴 타입은 항상 포트(ABC) 타입. 구현체 타입 노출 금지.
- `AsyncSession`은 `core.matrix.gird_oracle_database_manager.get_db`에서 주입.

---

## 새 캐릭터 추가 체크리스트

캐릭터 하나를 추가할 때 생성해야 하는 파일 목록 (순서는 안쪽 → 바깥쪽).

1. `app/dtos/piper_{x}_dto.py` — Query, Response 정의
2. `app/ports/input/piper_{x}_use_case.py` — Input Port (ABC)
3. `app/ports/output/piper_{x}_port.py` — Output Port (ABC)
4. `app/use_cases/piper_{x}_interactor.py` — UseCase 구현
5. `adapter/outbound/orm/piper_{x}_orm.py` — ORM 모델
6. `adapter/outbound/mappers/piper_{x}_mapper.py` — Mapper
7. `adapter/outbound/repositories/piper_{x}_repository.py` — Repository
8. `adapter/inbound/api/schemas/piper_{x}_schema.py` — Inbound Schema
9. `adapter/inbound/api/v1/piper_{x}_router.py` — Router
10. `dependencies/piper_{x}_provider.py` — DI 팩토리
