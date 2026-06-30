# GourmetMate 마이그레이션 계획

기획서(`GourmetMate_기획서.docx`) 기준 `apps/restaurant` + `apps/user` 마이그레이션
실행 계획과 순차 작업 목록. 상위 규칙은 [[fastapi/_docs/CLAUDE|Backend Docs]]를 먼저 읽는다.

---

## 확정 사항 (2026-06-28)

| 항목 | 결정 |
|------|------|
| 식당 데이터 소스 | **서울 CSV 새로 발급** (data.go.kr, 아직 미수령) |
| 서비스 지역 | 서울 한정 (기획서 6-3) |
| 폐업 식당 삭제 | **스크립트만 작성** — DB DELETE는 사용자가 직접 실행 |
| 날씨 API | **OpenWeather 유지** (기상청 전환 안 함) |
| 이번 턴 범위 | **빈 슬라이스 스캐폴드 + 계획** (구현은 아래 단계대로) |

---

## 기능 격차 (기획서 ↔ 현재 코드)

| 기획 기능 | 현재 | 담당 앱 | 신규 feature |
|-----------|------|---------|--------------|
| 온보딩 5단계 | 없음 | user | `onboarding` |
| 좋아요/싫어요/제외 학습 | 없음 | user | `taste_feedback` |
| GPS 방문확인 + 별점 | 없음 | user | `visit_rating` |
| 버짓 월말 리포트·실지출 | meal_plan 일부 | user | `budget_report` |
| 커플/여행 하루 코스 | 없음 | restaurant | `course_recommendation` |
| 헬스 식단 추천 | 없음 | restaurant | `diet_recommendation` |
| AI 개인화 추천 엔진 | gourmet_chat만 | restaurant | `personalized_recommendation` |

> **시간대 자동 감지·날씨 반영**은 `personalized_recommendation`의 입력 맥락
> (`time_slot`, `weather`)으로 흡수한다. 별도 feature 아님.

---

## 이번 턴에 완료한 작업

### 1. 스캐폴드된 계약 파일 (포트 + DTO, 미배선)

`user` 앱:

- `app/dtos/onboarding_dto.py` · `ports/input/onboarding_use_case.py` ·
  `ports/output/onboarding_repository.py`
- `app/dtos/taste_feedback_dto.py` · `ports/input/taste_feedback_use_case.py` ·
  `ports/output/taste_feedback_repository.py`
- `app/dtos/visit_rating_dto.py` · `ports/input/visit_rating_use_case.py` ·
  `ports/output/visit_rating_repository.py`
- `app/dtos/budget_report_dto.py` · `ports/input/budget_report_use_case.py` ·
  `ports/output/budget_report_repository.py`

`restaurant` 앱:

- `app/dtos/course_recommendation_dto.py` · `ports/input/...` · `ports/output/...`
- `app/dtos/diet_recommendation_dto.py` · `ports/input/...` · `ports/output/...`
- `app/dtos/personalized_recommendation_dto.py` · `ports/input/...` ·
  `ports/output/...`
- `app/use_cases/strategies/recommendation_scoring_strategy.py` (OCP)

> `personalized_recommendation`은 스포크→스포크 직접 import 금지 규칙에 따라
> user 취향을 `PreferenceSnapshot` DTO로 받는다. 변환·주입은 `main.py`에서만.

### 2. `.env.example` 추가

- `KAKAO_REST_API_KEY` — 카카오맵 (위치/좌표, 기획서 6-1)
- `RESTAURANTS_CSV` — 서울 식당 CSV 경로

기존 유지: `DATABASE_URL`, `GEMINI_API_KEY`, `OPENWEATHER_API_KEY`,
`OPENWEATHER_CITY`.

### 3. 폐업 정리 스크립트

`scripts/clean_closed_restaurants.py` — 기본 dry-run. CSV에서 폐업 행을 걸러
정제 CSV·폐업번호 목록·DELETE SQL을 생성한다. `--execute` 시에만 DB 삭제.

---

## 순차 작업 목록 (사용자 진행)

각 단계는 **검증**까지 끝나야 다음으로 넘어간다.

### 0단계 — 키·CSV 준비 (사용자 직접)

1. Kakao Developers에서 REST API 키 발급 → `.env`에 `KAKAO_REST_API_KEY` 입력.
2. data.go.kr에서 **서울 일반음식점 인허가 CSV**(영업상태명 컬럼 포함) 다운로드.
3. `.env`의 `RESTAURANTS_CSV`에 절대경로 입력.
   - 검증: `python -c "import os;print(os.path.exists(os.environ['RESTAURANTS_CSV']))"`

### 1단계 — 폐업 정리

1. `python scripts/clean_closed_restaurants.py` (dry-run) 실행.
2. 출력된 헤더가 스크립트 상단 상수(`COL_BIZ_NUMBER`,`COL_STATUS`)와 맞는지 확인,
   다르면 상수 수정 후 재실행.
   - 검증: `*.active.csv` / `*.delete_closed.sql` 생성, 영업/폐업 건수 로그 확인.
3. 기존 DB에 적재분이 있으면 생성된 `*.delete_closed.sql`을 검토 후 직접 실행
   (또는 `--execute`).

### 2단계 — 데이터 적재 (정제 CSV → restaurants)

1. 정제된 `*.active.csv`를 `RESTAURANTS_CSV` 경로로 교체.
2. 기존 ingestion(`data/ingestion/base_restaurant_importer.py`) 컬럼 매핑이
   서울 인허가 CSV 헤더와 다르면 `restaurant_row_cleaner.py` 조정.
   - 검증: `replace_all=True` import 후 `SELECT count(*) FROM restaurants`.

### 3단계 — 온보딩 (user / `onboarding`)

1. ORM `user_preferences` + Alembic 마이그레이션.
2. `OnboardingRepository` 구현(`adapter/outbound/pg/...`) + `OnboardingInteractor`.
3. `dependencies/onboarding_provider.py` (`get_onboarding_use_case`).
4. 라우터 + 스키마, `user/adapter/inbound/api/v1/__init__.py`에 등록.
   - 검증: 온보딩 POST → GET 라운드트립 테스트 통과.

### 4단계 — 취향 피드백 (user / `taste_feedback`)

1. ORM `taste_feedbacks`(restaurant_id, signal, time_slot, weather) + 마이그레이션.
2. Repository + Interactor + provider + 라우터.
   - 검증: dislike 기록 → `excluded_restaurant_ids` 반영 테스트.

### 5단계 — 방문/별점 (user / `visit_rating`)

1. ORM `restaurant_visits`(rating, lat/lng) + 마이그레이션.
2. Repository + Interactor + provider + 라우터.
   - 검증: 방문 확인 + 별점 저장 테스트.

### 6단계 — 개인화 추천 엔진 (restaurant / `personalized_recommendation`)

1. `PersonalizedRecommendationRepository` 구현(제외 식당 필터 포함).
2. `RecommendationScoringStrategy` 구체 전략 1개(시간대·날씨·취향 가중치).
3. Interactor + provider + 라우터(메인 홈 1곳, "마음에 안 들어" 재추천).
4. `main.py`에서 user 취향 → `PreferenceSnapshot` 조립 주입.
   - 검증: 제외 식당이 추천에서 빠지는지, time_slot별 응답 차이 테스트.

### 7단계 — 버짓 리포트 (user / `budget_report`)

1. ORM `meal_plan_expenses` + 마이그레이션, meal_plan 잔여 차감 연동.
2. Repository(집계) + Interactor + provider + 라우터.
   - 검증: 지출 입력 → 잔여 차감 → 월말 리포트 합계 테스트.

### 8단계 — 탭 추천 (restaurant / `course_recommendation`, `diet_recommendation`)

1. 태그/카테고리 기반 Repository 2종 + Interactor 2종.
2. provider + 라우터(커플/여행 코스, 헬스 식단).
   - 검증: 지역 입력 시 슬롯별 코스 구성, 식단 태그 필터 테스트.

### 9단계 — 하네스 검증

1. `python scripts/validate_harness.py`
2. `lint-imports --config .importlinter` (스포크→스포크 위반 0)
3. `markdownlint --config .markdownlint.yaml "**/*.md"`
   - 검증: 3개 모두 통과.

---

## 미해결·확인 필요

- 서울 인허가 CSV의 정확한 컬럼명 — 수령 후 ingestion 매핑/스크립트 상수 확정.
- 기존 Neon DB의 식당 적재 여부 — 있으면 1단계 DELETE 대상, 없으면 2단계만.
- ERD 갱신 — 신규 테이블 5종 반영은 각 단계에서 `gourmetmate_v2_erd.md` 수정.

---

## 관련 문서

[[fastapi/_docs/CLAUDE|Backend Docs]]
