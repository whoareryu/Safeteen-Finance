# Backend 엔티티·테이블 규칙 (GourmetMate)

`backend/**` 에서 ORM 모델·DB 테이블을 추가·수정할 때 따르는 **기본 키(PK) 규칙**입니다.  
에이전트는 `docs/README.md` → **본 문서**를 읽은 뒤 `apps.database.Base` 를 상속하는 모델을 작성합니다.

---

## 1. 기본 원칙 (필수)

| 항목 | 규칙 |
|------|------|
| PK 타입 | **`int`** (정수) |
| PK 컬럼명 | **`id`** 로 통일 (다른 이름 금지: `user_id`, `pk`, `uuid` 등을 PK로 쓰지 않음) |
| 생성 방식 | DB **자동 증가** (`autoincrement` / `SERIAL` / `IDENTITY`) |
| 용도 | 시스템 내부용 **대리 키(surrogate key)** — 비즈니스 식별은 별도 컬럼(`username`, `name` 등) |

**금지**

- UUID·문자열·복합키를 **기본 키**로 사용
- 테이블마다 PK 이름을 다르게 짓기 (`restaurant_pk`, `member_no` 등)
- `id` 없이 NATURAL KEY 만으로 테이블 정의

**다른 테이블 참조(FK)** 는 `{엔티티}_id` 형태의 **int** 컬럼을 쓰고, 참조 대상은 항상 **`{테이블}.id`** 입니다.

```python
restaurant_id: Mapped[int] = mapped_column(
    ForeignKey("restaurants.id", ondelete="CASCADE"),
    index=True,
)
```

---

## 2. 참조 코드 — SQLModel (`Field`)

SQLModel 을 쓰는 경우에도 PK 이름·타입은 동일합니다.

```python
from typing import Optional

from sqlmodel import Field, SQLModel


class ExampleEntity(SQLModel, table=True):
    __tablename__ = "examples"

    # 시스템 내부용 자동 증감 고유 번호 (기본 키)
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"name": "id"},  # DB 컬럼명: id
    )
```

- `default=None` + `primary_key=True` → INSERT 시 DB가 번호 부여
- `sa_column_kwargs={"name": "id"}` → ORM 속성명·DB 컬럼명 모두 **`id`**

---

## 3. 참조 코드 — SQLAlchemy 2.0 (본 프로젝트 표준)

이 저장소의 ORM은 `apps.database.Base` + `Mapped` / `mapped_column` 패턴을 **기본**으로 합니다.

**공통 기본 키:** `apps.database.IntIdPrimaryKeyMixin` — 모든 테이블 모델이 상속한다.

```python
from apps.database import Base, IntIdPrimaryKeyMixin


class ExampleEntity(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "examples"
    # id 는 믹스인에서 제공 (int, autoincrement, 컬럼명 id)

    title: Mapped[str] = mapped_column(String(128))
```

직접 한 줄로 쓸 때는 다음과 동등하다.

```python
id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, sort_order=-1000)
```

### 프로젝트 내 적용 예

| 테이블 | 모델 | PK |
|--------|------|-----|
| `users` | `apps.auth.user_model.User` | `IntIdPrimaryKeyMixin` 상속 |
| `restaurants` | `apps.gourmet.app.models.restaurant.Restaurant` | 동일 |
| `daily_picks` | `apps.gourmet.app.models.daily_pick.DailyPick` | 동일 |
| `search_query_logs` | `apps.gourmet.app.models.search_query_log.SearchQueryLog` | 동일 |
| `restaurant_view_stats` | `apps.gourmet.app.models.restaurant_view_stat.RestaurantViewStat` | 동일 |

새 테이블도 위와 **동일한 한 줄 PK** 로 시작합니다.

---

## 4. 새 모델 체크리스트

- [ ] `class Xxx(IntIdPrimaryKeyMixin, Base):` + `__tablename__` 정의
- [ ] PK `id`는 **믹스인**으로만 정의하거나, 단독 모델이면 `id: Mapped[int]` + `autoincrement=True` + `sort_order=-1000` (첫 컬럼 보장)
- [ ] FK는 `*_id: Mapped[int]` + `ForeignKey("other_table.id")` 인가?
- [ ] `database.py` 의 `_register_orm_models` / `create_all` 대상에 모델이 등록되는가?
- [ ] 기존 DB에 테이블이 있으면 `ALTER TABLE ... ADD COLUMN` 이 아니라 **새 테이블**은 `create_all` 또는 마이그레이션으로 `id` 컬럼이 포함되는가?

---

## 5. 에이전트 표준 프롬프트 (복사용)

```text
@docs/DevOps/Backend/ENTITY_RULE.md 규칙을 따르세요.
모든 테이블은 int 자동 증가 기본 키이며 컬럼명은 id 로 통일합니다.
SQLAlchemy Mapped 패턴으로 apps.database.Base 상속 모델을 작성해 주세요.
```

---

## 관련 문서

[[whoareryu/_claude/CLAUDE\|Backend CLAUDE]] · [[GOURMET_ERD]] · [[gourmetmate_v2_erd]]
