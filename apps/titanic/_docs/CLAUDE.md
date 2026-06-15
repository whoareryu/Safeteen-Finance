# CLAUDE.md — Titanic 앱

Titanic 앱 전용 규약. 상위 규칙은 [../../CLAUDE.md](../../CLAUDE.md)(백엔드) → [../../../../CLAUDE.md](../../../../CLAUDE.md)(루트) 순으로 읽는다.

---

## 앱 개요

Titanic 생존자 데이터를 기반으로 한 ML 파이프라인 앱.  
백엔드 헥사고날 아키텍처의 **레퍼런스 구현** — 새 앱 추가 시 이 구조를 복제한다.

- DB: **async** `AsyncSession` + `get_db` (Neon PostgreSQL)
- prefix: `/titanic`
- import 루트: `titanic.*`

---

## 디렉터리 구조

```text
titanic/
├── _docs/
│   └── CLAUDE.md               # 이 파일
├── adapter/
│   ├── inbound/api/
│   │   ├── __init__.py          # titanic_router 집계
│   │   ├── schemas/             # Pydantic (HTTP 경계)
│   │   └── v1/                  # feature 라우터
│   └── outbound/
│       ├── orm/                 # SQLAlchemy ORM
│       └── pg/                  # PgRepository 구현체
├── app/
│   ├── dtos/                    # Command / Query (dataclass)
│   ├── ports/
│   │   ├── input/               # UseCase ABC
│   │   └── output/              # Repository ABC
│   └── use_cases/               # Interactor 구현체
├── dependencies/                # DIP 팩토리
├── domain/                      # (예약) 순수 엔티티·VO
└── tests/
```

---

## Feature 슬라이스 현황

### James Director — 완성 슬라이스 (레퍼런스)

CSV 업로드 → 배치 INSERT 파이프라인.

| 파일 | 역할 |
|------|------|
| `adapter/inbound/api/v1/james_director_router.py` | CSV 업로드, `_parse_csv` |
| `adapter/inbound/api/schemas/james_director_schema.py` | `JamesDirectorSchema`, 응답 스키마 |
| `app/ports/input/james_director_use_case.py` | `JamesDirectorUseCase` |
| `app/ports/output/james_director_repository.py` | `JamesDirectorRepository` |
| `app/use_cases/james_direcrtor_interactor.py` | `JamesDirectorInteractor` (**파일명 typo** — `direcrtor`) |
| `app/dtos/james_director_dto.py` | `PassengerCommand`, `BookingCommand` |
| `adapter/outbound/pg/james_director_pg_repository.py` | 배치 INSERT (500건 단위) |
| `adapter/outbound/orm/person_orm.py`, `booking_orm.py` | `titanic_persons`, `bookings` 테이블 |
| `dependencies/james_director.py` | `get_james_director_use_case(db)` |

- endpoint: `POST /titanic/james/upload`
- 타임아웃 방지를 위해 500건 단위 배치 커밋

### Jack Trainer — 생존 예측 (진행 중)

| 파일 | 역할 |
|------|------|
| `adapter/inbound/api/v1/passenger_jack_trainer_router.py` | `GET /titanic/jack/myself` |
| `adapter/inbound/api/schemas/passenger_jack_trainer_schema.py` | `JackTrainerSchema` |
| `app/ports/input/passenger_jack_trainer_use_case.py` | `JackTrainerUseCase` |
| `app/ports/output/passenger_jack_trainer_repository.py` | `JackTrainerRepository` |
| `app/use_cases/passenger_jack_trainer_interactor.py` | `JackTrainerInteractor` |
| `dependencies/passenger_jack_trainer_provider.py` | `get_jack_trainer_use_case()` |

### Walter Roaster — 진행 중

- `dependencies/walter_roaster.py`, `walter_roaster_router.py` DIP 골격 있음.
- Input port / interactor / schema 일부 미완·import 경로 정리 필요.

---

## 개발 백로그

### 진행 중 / 다음 작업

- [ ] **Walter** ports + interactor + schema + DIP 라우터 연결
- [ ] **James** `james_direcrtor_interactor.py` 파일명 오타 수정 (import 전역 영향 — 신중히)
- [ ] **레거시** `app/james_controller.py`, `jack_service.py`, `walter_reader.py` 정리 또는 문서화
- [ ] **ORM** `import_models()`에 Titanic ORM 경로 반영 확인

### 알려진 이슈

| 이슈 | 내용 |
|------|------|
| James 파일명 typo | `james_direcrtor_interactor.py` — `direcrtor` 오타. import 전체 영향으로 수정 시 신중히 |
| Titanic ORM 경로 | `person_orm`/`booking_orm` 등 일부 경로는 import 기대와 디스크 불일치 가능 — 작업 전 `import titanic...` 확인 |
| 레거시 컨트롤러 | `main.py`의 `titanic.app.james_controller` import는 레거시, 실제 라우팅은 `titanic_router` |

---

## 새 feature 추가 체크리스트

James Director 슬라이스를 복제해서 시작한다.

```
1. adapter/inbound/api/schemas/{feature}_schema.py
2. adapter/inbound/api/v1/{feature}_router.py
3. app/ports/input/{feature}_use_case.py
4. app/ports/output/{feature}_repository.py
5. app/dtos/{feature}_dto.py
6. app/use_cases/{feature}_interactor.py
7. adapter/outbound/pg/{feature}_pg_repository.py
8. adapter/outbound/orm/{entity}_orm.py  (신규 테이블 시)
9. dependencies/{feature}.py
10. adapter/inbound/api/__init__.py 에 라우터 등록
```

검증:
```powershell
cd whoareryu
$env:PYTHONPATH="$PWD;$PWD\apps"
python -c "from titanic.adapter.inbound.api import titanic_router; print('ok')"
```

---

## 관련 문서

[[whoareryu/_claude/CLAUDE\|Backend CLAUDE]] · [[whoareryu/apps/titanic/_docs/james_code_review\|james_code_review]] · [[whoareryu/apps/titanic/_docs/titanic_architecture\|titanic_architecture]] · [[TITANIC_ERD]]
