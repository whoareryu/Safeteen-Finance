# (구 문서) FastAPI 코드 리뷰 — `app/james.py`

이 문서는 **`JamesController` / `app/james.py` 제거** 로 더 이상 유효하지 않습니다.

**현재 구조는 아래 문서를 참고하세요.**

→ [[whoareryu/apps/titanic/_docs/titanic_architecture|Titanic 백엔드 — 헥사고날 구조]] · [[whoareryu/apps/titanic/_docs/CLAUDE|Titanic CLAUDE]] · [[whoareryu/_claude/CLAUDE|Backend CLAUDE]]

---

## 요약 (마이그레이션)

| 이전 | 현재 |
|------|------|
| `app/james.py`, `james_controller.py` | 삭제 |
| `James` / `JamesController` 래퍼 | `TitanicQueryUseCase` |
| `main.py` 의 `@app.get("/titanic/...")` | `titanic_query_router.py` |
| `uvicorn.run("app.james:app", ...)` | `uvicorn main:app` (`backend/apps`) |
| `Walter` 직접 호출 | `WalterReader` → `JackService` → `TitanicReadPort` |

과거 리뷰 원문(미사용 `James` 클래스, 요청마다 `Walter()` 생성 등)은 Git 히스토리에서 확인할 수 있습니다.
