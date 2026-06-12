# Titanic 백엔드 — 헥사고날 구조

> **2026-05** `JamesController` / `app/james.py` / `james_controller.py` 는 제거되었습니다.  
> 조회 책임은 **`TitanicQueryUseCase`** 와 **`titanic_query_router`** 로 이전되었습니다.

---

## 레이어 구조

```
[Inbound Adapter]  adapter/inbound/api/v1/titanic_query_router.py
        │  Depends(get_titanic_query_use_case)
        ▼
[Use Case]         app/use_cases/titanic_query_impl.py  (TitanicQueryUseCase)
        │  TitanicQueryPort (input)
        │  TitanicReadPort (output, DI)
        ▼
[Application]      app/use_cases/jack_service.py
        ├─ app/use_cases/walter_reader.py     (CSV 읽기)
        ├─ app/use_cases/cal_tester.py
        └─ app/models/rose_model.py           (결정 트리·정확도)
```

**커맨드(채팅)** 는 별도 축입니다.

- `titanic_command_router.py` → `TitanicCommandUseCase` → Gemini + DB 컨텍스트

**앱 등록**

- `backend/apps/main.py` 에서 `apps.titanic.adapter.inbound.api.v1.router` 를 `include_router`

---

## 조회 API (`GET /titanic/...`)

| 경로 | 설명 |
|------|------|
| `/titanic/data` | 첫 승객 1행 (dict) |
| `/titanic/count` | `{"count": N}` |
| `/titanic/count/survived` | `{"survived": N}` |
| `/titanic/count/dead` | `{"dead": N}` |
| `/titanic/tree` | `{"has_decision_tree_model": bool}` |
| `/titanic/model`, `/titanic/model_name` | `{"model_name": str}` |
| `/titanic/accuracy` | `{"accuracy": float}` |

CSV가 없으면 **404** 와 안내 메시지를 반환합니다.

**데이터 파일 위치**

- `backend/apps/titanic/app/data/Titanic-Dataset.csv`

---

## 유스케이스 (기존 JamesController 메서드 대응)

| 이전 (JamesController) | 현재 (TitanicQueryUseCase) |
|------------------------|----------------------------|
| `get_data()` | `get_data()` |
| `get_count()` | `get_count()` |
| `get_count_survived()` | `get_count_survived()` |
| `get_count_dead()` | `get_count_dead()` |
| `has_decision_tree_model()` | `has_decision_tree_model()` |
| `get_training_model_name()` | `get_training_model_name()` |
| `get_training_model_accuracy()` | `get_training_model_accuracy()` |

테스트·모킹 시 포트만 교체합니다.

```python
from apps.titanic.app.use_cases.titanic_query_impl import TitanicQueryUseCase

use_case = TitanicQueryUseCase(reader=mock_reader)
```

---

## 서버 실행

```bash
cd backend/apps
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

문서/UI: `http://127.0.0.1:8000/docs`

> 예전 단일 모듈 진입점 `uvicorn.run("app.james:app", ...)` 는 더 이상 사용하지 않습니다.

---

## 설계 메모 (과거 리뷰 반영)

| 항목 | 권장 | 현재 |
|------|------|------|
| 컨트롤러 래퍼 | 유스케이스로 통합 | `TitanicQueryUseCase` |
| CSV 읽기 | 유스케이스 레이어 | `use_cases/walter_reader.py` |
| 모델·정확도 | 도메인/서비스 분리 | `RoseModel` + `JackService` |
| HTTP 라우트 | 어댑터 전용 | `titanic_query_router` |
| CSV 없음 | 명시적 404 | `_csv_missing` 핸들러 |

---

## 관련 파일

| 역할 | 경로 |
|------|------|
| Query 라우터 | `backend/apps/titanic/adapter/inbound/api/v1/titanic_query_router.py` |
| Command 라우터 | `backend/apps/titanic/adapter/inbound/api/v1/titanic_command_router.py` |
| Query 유스케이스 | `backend/apps/titanic/app/use_cases/titanic_query_impl.py` |
| Input port | `backend/apps/titanic/app/ports/input/titanic_query_port.py` |
| Output port | `backend/apps/titanic/app/ports/output/titanic_read_port.py` |

---

## 관련 문서

[[whoareryu/apps/titanic/_docs/CLAUDE\|Titanic CLAUDE]] · [[whoareryu/_claude/CLAUDE\|Backend CLAUDE]] · [[TITANIC_ERD]] · [[whoareryu/apps/titanic/_docs/james_code_review\|james_code_review]]
