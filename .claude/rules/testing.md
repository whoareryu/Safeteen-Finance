# 테스트 규칙

도메인마다 프레임워크와 검증 수단이 다르다.

---

## fastapi — pytest

- 설정: `fastapi/pytest.ini` (`asyncio_mode = auto`, `pythonpath = . apps`, `testpaths = apps`)
- 위치: `fastapi/apps/<앱명>/tests/` — 현재 `admin`/`auth`/`community`/`ontology`/`plant`/
  `soccer`/`dumb_and_dumber`에 존재.
- **단위 테스트는 DB 없이 돌아야 한다** — `domain/`, `app/use_cases/` 레이어는 리포지터리를
  목(mock)/페이크로 대체해서 테스트한다. DB가 필요한 테스트는 어댑터(`adapter/outbound/`)
  레이어에만 둔다.
- `ollama` 마커가 붙은 테스트는 로컬 Ollama 서버(+해당 모델 pull)가 필요하다.
  기본은 `addopts = -m "not ollama"`로 제외되므로, 실행하려면
  `python -m pytest -m ollama`를 명시한다.
- 실행:
  ```bash
  cd fastapi
  python -m pytest                          # 전체
  python -m pytest apps/ontology/tests/ -v  # 앱별
  ```
- **TDD 우선** — 새 유스케이스를 추가할 때는 실패하는 테스트를 먼저 쓰고(Red),
  구현으로 통과시킨 뒤(Green), 정리한다(Refactor).

---

## flutter — `flutter test`

- 위치: `flutter/test/`
- 실행: `cd flutter && flutter test` (+ `flutter analyze`로 정적 분석)

---

## www — 테스트 하네스 없음

- `www/package.json`에 `test` 스크립트가 없고, ESLint 설정 파일도 없어 `pnpm lint`는
  동작하지 않는다.
- **변경 검증 수단은 `pnpm build`뿐이다.** "테스트 통과"를 성공 기준으로 요구하지 않는다.
- 테스트 하네스가 필요하다는 요청이 오면, 먼저 어떤 프레임워크(Vitest/Playwright 등)를
  도입할지부터 사용자에게 확인한다 — 임의로 고르지 않는다.
