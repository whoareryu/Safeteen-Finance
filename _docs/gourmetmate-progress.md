# GourmetMate 진행 현황 / 인계 노트

마지막 갱신: 2026-06-28. 상위 계획은 [[fastapi/_docs/gourmetmate-migration-plan|마이그레이션 계획]].

**가드레일(불변):** 수업 폴더 `apps/titanic`·`apps/silicon_valley`·`apps/star_craft`,
프론트 `app/portfolio/**`·`titanic-*`·`agent(s)-*`·`lesson-*`·`himedia-*`·
`neon-flow-lines`·`portfolio-project-tiles` 는 **건드리지 않는다.**

---

## ✅ 완료

### 데이터 적재
- 서울 식당 CSV → Neon `restaurants` 108,959건(+contacts 38,680). 마스터(food_categories 9·sigungu 25구·biz 644) 매핑 완료. 로더: `scripts/load_seoul_restaurants.py`.

### [1순위] 메인 홈 — 오늘의 추천 1곳 (규칙기반)
- 백엔드: `POST /gourmet/recommendation/today` (restaurant 슬라이스 8파일 + `__init__` 등록). `ContextScoringStrategy`(취향·시간대·날씨).
- 프론트: `components/today-recommendation.tsx`, `components/genre-restaurant-card.tsx`, `lib/gourmet-recommendation.ts`, `app/page.tsx` 마운트. tsc 0.

### 카카오맵
- 프론트: `components/kakao-map.tsx`·`lib/kakao-map-loader.ts`·`types/kakao-maps.d.ts`, 식당 상세 주소 아래 임베드. env `NEXT_PUBLIC_KAKAO_MAP_KEY`.
- 백엔드: `KAKAO_REST_API_KEY`(기존 `kakao_local_client.py`). **할 일: fastapi/.env 의 REST 키 실제 값 교체 + 카카오 콘솔에 Web 도메인 등록.**

### [2순위] 온보딩 — 완료 (백엔드 + 프론트)

프론트(2026-06-28 추가): `www/lib/gourmet-onboarding.ts`(X-User-Id) ·
`www/components/onboarding-wizard.tsx`(5단계+프로그레스바, 장르순위 ▲▼ 정렬) ·
`www/app/onboarding/page.tsx` · `www/components/onboarding-gate.tsx`(미완료 시
`/onboarding` 유도, `/portfolio`·`/onboarding` 제외) · `app/layout.tsx` 마운트. tsc 0.

#### (참고) 백엔드 상세
- DB: Neon `user_preferences` 테이블 생성(가산). 컬럼: user_id(FK,uniq)·genre_ranking(jsonb)·dining_mode·portion·allergies(jsonb)·avoid_foods(jsonb)·use_budget·monthly_budget.
- 코드: `user/adapter/outbound/orm/user_preference_orm.py`, `.../pg/onboarding_pg_repository.py`, `app/use_cases/onboarding_interactor.py`, `dependencies/onboarding_provider.py`, `adapter/inbound/api/schemas/onboarding_schema.py`, `.../v1/onboarding_router.py`, `api/__init__.py` 등록.
- API (인증: `X-User-Id` 헤더):
  - `GET  /gourmet/onboarding/me` → `{ completed, genre_ranking, dining_mode, portion, allergies, avoid_foods, use_budget, monthly_budget }`
  - `POST /gourmet/onboarding` (body 동일 필드) → 위 응답

---

### [3순위] AI 채팅 플로팅 버튼 — 완료

- `www/components/floating-chat.tsx`: 우하단 💬 토글 버튼 + 패널(기존 `gemini-chat`
  재사용, `apiPath="/api/gourmet/chat"` 맛집 RAG). 닫아도 홈 추천 유지(패널만 숨김).
  `/portfolio`(수업)에선 `usePathname`로 렌더 안 함.
- `app/layout.tsx` 마운트. tsc 0.

### [4순위] (A) 커플·여행 코스 + 헬스 식단 + 탭바 — 완료
- 백엔드(restaurant): `course_recommendation`(GET `/gourmet/course?district=&party_type=`,
  슬롯 브런치→점심→카페→저녁→술집) · `diet_recommendation`(GET `/gourmet/diet?diet_type=&district=`,
  diet_type→slug 휴리스틱: high_protein=[hansik,ilsik,yangsik]·low_carb=[ilsik,yangsik,asian]).
  각 interactor/pg_repo/provider/schema/router + `api/__init__` 등록. (신규 테이블 없음)
- 프론트: `components/bottom-tab-bar.tsx`(홈/커플·여행/헬스식단/버짓/마이, `/portfolio` 제외) ·
  `app/couple-travel/`·`app/health-diet/`(genre-restaurant-card 재사용)·`app/budget/`(플레이스홀더) ·
  `lib/gourmet-tabs.ts` · `app/layout.tsx` 마운트(+플로팅챗 위치 상향). tsc 0.

### [4순위] (B) 버짓 — 완료 (자체 완결형)
- 백엔드(user): `budget_report` 슬라이스 + ORM `meal_plan_expenses` + Neon 테이블(가산).
  엔드포인트: `GET/PUT /gourmet/budget/plan`(월예산 설정·조회), `POST /gourmet/budget/expense`
  (지출 입력→`meal_plans.spent_amount` 누적), `GET /gourmet/budget/report?meal_plan_id=`
  (total_spent·saved·top_restaurants·top_categories, restaurants/food_categories 조인). 조인 SQL 검증.
- 프론트: `app/budget/page.tsx`(예산설정·남은예산·하루 사용가능·지출입력·월말리포트) +
  `lib/gourmet-budget.ts`. tsc 0.
- 기존 buggy `meal_plan` feature에 의존하지 않도록 버짓이 plan 생성/조회를 자체 처리.

## 🐞 버그 (모두 수정됨)
- ✅ `meal_plan_interactor.py` `self._user`→`self._meal_plans`(2곳). `/gourmet/meal-plans/*` 복구.
- ✅ `meal_plan_router` 조회 엔드포인트(`/me/current`, `/users/{id}/current`): 플랜 없을 때
  500 대신 **200 + null** 반환(`response_model=MealPlanResponse | None`, plan 없으면 None).

### [5순위] GPS 방문 감지 — 완료
- 백엔드(user): `visit_rating` 슬라이스 + ORM `restaurant_visits` + Neon 테이블.
  `POST /gourmet/visits`(restaurant_id·rating 1~5·lat·lng).
- 프론트: `lib/gourmet-visit.ts`(추천 식당 localStorage 타깃 저장 + 방문 API) ·
  `components/visit-detector.tsx`(watchPosition 반경 200m → 팝업 → 별점 + 선택 지출,
  버짓 플랜 있으면 지출 자동 반영) · `today-recommendation` 이 추천 시 타깃 기록 ·
  layout 마운트(`/portfolio` 제외). tsc 0.
  - 한계: 웹은 앱 열려있을 때만 위치 감지(백그라운드 X) — 사양대로.

## 🎉 1~5순위 전부 완료

신규 Neon 테이블(가산, 비파괴): `user_preferences` · `meal_plan_expenses` · `restaurant_visits`.
(식당 데이터는 앞서 `restaurants` 108,959건 교체 적재 완료.)

**Alembic 버전관리**: `alembic/versions/f1a2b3c4d5e6_add_gourmet_user_tables.py`
(down=`b1c2d3e4f5a6`). upgrade 멱등(존재 시 skip)이라 운영 DB엔 데이터 보존하며 버전만 전진,
fresh DB엔 실제 생성. **멀티헤드 정리(완료)**: 기존 3 head(titanic `20250604_0001`, gourmet `e7f8a9b0c1d2`,
`f1a2b3c4d5e6`)를 merge 마이그레이션 `3462e2ac1573_merge_gourmet_titanic_heads.py`
(upgrade/downgrade 빈 mergepoint)로 단일화. 운영 DB는 브랜치 DDL 재실행 없이
`alembic stamp 3462e2ac1573` 로 기록(테이블 무변경 — titanic 보존 확인).
현재 `alembic current = 3462e2ac1573 (head)`, head 1개 → 이제 `alembic upgrade head` 정상.

실행 메모: 콘솔 스크립트 shebang 깨짐 → `python -m alembic` 사용. asyncpg(async) 기반이라 psycopg2 불필요.

### 대청소: 비스펙 기능 제거 (진행 중)
- ✅ **즐겨찾기(favorites)**: user 슬라이스 9파일 + 프론트(별버튼·provider·lib·mypage/favorites) 삭제,
  layout/header/nav/sidebar/card/detail 참조 정리. DB `favorites` drop (Alembic `c1f2a3d4b5e6`).
- ✅ **조회수(view_count)**: restaurant `view_stat` 슬라이스 10파일 + `restaurant_view_stat_orm` 삭제,
  gourmet_router view 엔드포인트 3개·gourmet_schema 응답 2클래스 제거, `restaurant_orm.view_count`
  컬럼·detail dict 제거, 프론트 표시·`recordRestaurantView` 제거. DB `restaurants.view_count`
  컬럼 drop (Alembic `d2e3f4a5b6c7`). tsc 0, ORM↔DB 일치 확인.
- ✅ **미사용 `/myself` 스텁 라우터 17개 삭제** + `restaurant/api/__init__` 실라우터 9개만 유지
  (catalog·gourmet_chat·gourmet·restaurant_v2·admin·weather·course·diet·personalized). 라우트 40→23.
  주의: 스텁 슬라이스의 interactor/repo는 gourmet/catalog/meal_plan이 실사용 → **라우터만 제거, 구현 보존**.
  완전 고아인 `restaurant_profile` 슬라이스만 8파일 통째 삭제.
- ✅ **프론트 브라우즈/카테고리 UI 대청소**: 홈→오늘의추천만, layout에서 CategoryMenuProvider·
  CategorySidebarDrawer 제거, header 카테고리 버튼 제거, 상세 카테고리 링크 제거(라벨만).
  브라우즈 페이지 삭제(app/food·stores·topics), 브라우즈 컴포넌트 15개 삭제(hero-section·
  category-*·home-topic-feed·topic-*·today-daily-pick·todays-picks-carousel·gourmet-mate-hero·
  gourmet-nav-search·infinite-scroll-sentinel). `browse-shell-layout`(단순 래퍼)은 상세가 써서 유지.
  백엔드 고아 `gourmet_chat_schema.py` 삭제. tsc 0, 백엔드 임포트 정상.
- ✅ **백엔드 브라우즈 엔드포인트 수술**: gourmet_router를 상세 2개(official-store·restaurants/{id})만
  남기고 browse/search/categories/topics/daily-pick/today-picks 6개 제거. catalog_router 삭제·등록 해제.
  restaurant_router(v2)의 categories 브라우즈 제거(상세만 유지). 최종 GourmetMate 엔드포인트 20개,
  브라우즈/검색 0개. 임포트 정상.
  주의: 슬라이스 interactor(category_browse/home_browse/search 등)는 detail/chat/meal_plan과
  전이적으로 엮여 **파일은 보존**(내부 dead code). gourmet_schema의 미사용 응답클래스, 프론트 lib의
  미사용 helper(gourmet-topics 등)도 잔존(무해).

### UI: 이미지 카드 → 장르 카드 (완료)
서울 CSV엔 사진이 없어 `image_url`이 빈 값 → 이미지 카드 깨짐. 공용 장르 스타일
`www/lib/genre-style.ts`(slug/label→그라디언트·이모지) 신설 후 교체:
`restaurant-card.tsx`(food/topics/stores/search/캐러셀 전반) · `genre-restaurant-card.tsx`
(공용맵 사용, 바·카페·디저트·기타 라벨 정상화) · `restaurant-detail-page.tsx` 헤더. tsc 0.
(`mypage/favorites`는 `/placeholder.svg` 폴백이 있어 미교체 — 깨지지 않음.)

### 선택 후속 (모두 완료)
- ✅ 홈 추천 ↔ 온보딩 취향 연결: `today-recommendation` 이 로그인 시
  `GET /gourmet/onboarding/me` 의 `genre_ranking` 을 추천 요청에 전달 → 점수 반영.
- ✅ meal_plan 버그 2건 수정(아래 🐞).
- ✅ 식당 보강: `scripts/enrich_restaurants.py`(휴리스틱·멱등). `restaurant_prices` 108,959
  (카테고리별 추정 식대) + `restaurant_tags` 190,495(든든한·가성비·분위기·혼밥·데이트) 적재.
  → 카드 avg_price·ai_tags 표시, 버짓 per-meal-cap 동작, 식단/주제 필터 품질 향상.
  메뉴명은 실데이터 없어 미생성.

### 미연결(소규모 후속, 선택)
- 홈 추천(`today-recommendation`)이 온보딩 `genre_ranking` 을 아직 안 보냄.
  로그인 사용자면 `GET /gourmet/onboarding/me` 의 `genre_ranking` 을 추천 요청
  `genre_ranking` 에 실으면 취향 반영됨.

---

## 환경/검증 메모
- 로컬엔 psycopg2 없음 → 동기 엔드포인트 로컬 직접 실행 불가. 로직/SQL 은 별도 검증. 실제 동작은 백엔드 런타임(Docker).
- Neon 접속: `venv/bin/python` + asyncpg, `ssl="require"`, URL 쿼리스트링 제거 후 연결.

## 🧹 SOLID/헥사고날 리팩터링 (수업 폴더 제외)
하네스 규칙 점검 후 위반 수정. **수업(titanic·star_craft·silicon_valley) 무수정.**

수정 결과(before→after):
- ✅ **스포크 순환결합 restaurant↔user: 다수(양방향) → 0**. 구버전 `meal_plan`·`daily_pick`·
  `restaurant_domain`·`recommendation_strategy` 클러스터 제거(budget_report·personalized로 대체됨),
  `meal_plan_orm`의 UserOwnedEntityMixin(cross-spoke) 제거, `interfaces.py`(cross-spoke 재export) 삭제.
- ✅ **ORM→app 역참조: 1 → 0**. 거리계산을 `restaurant/domain/location.py`(도메인 레이어 신설)로 이동.
- ✅ **포트→adapter: 19 → 2**, **app/use_cases→adapter: 다수 → 8**. 죽은 `/myself` 스텁 슬라이스 +
  restaurant_browse/search의 죽은 Interactor 클래스·포트·스키마 제거(살아있는 함수는 유지).
- 총 ~55개 dead/coupling 파일 삭제. 신규 슬라이스(personalized/onboarding/budget/visit/course/diet)는
  포트가 DTO만 의존(ISP 준수)·스포크 결합 회피.

남은 위반(레거시, chat/detail/browse 동작 코드 — 도메인 모델·리포지토리 리팩터링 필요):
- 포트→adapter 2: `restaurant_detail_use_case`(죽은 introduce_myself 스텁 스키마), `restaurant_repository`(→Restaurant ORM, 도메인 엔티티 부재).
- app→adapter 8: `restaurant_browse`(쿼리를 app에서 ORM 직접) · `gourmet_chat`/`restaurant_detail`(포트 대신 구현 직접 import, DIP) · `coordinates_sync`.
- `domain/` 레이어는 location 외 여전히 빈약(anemic) — 도메인 모델화는 별도 과제.
- import-linter 미설치(계약 정적검증 불가) → 설치 권장. 일부 _docs MD frontmatter `type:` 누락.

## 관련 문서
[[fastapi/_docs/gourmetmate-migration-plan|마이그레이션 계획]] · [[fastapi/CLAUDE|Backend CLAUDE]] · [[www/CLAUDE|Frontend CLAUDE]]
