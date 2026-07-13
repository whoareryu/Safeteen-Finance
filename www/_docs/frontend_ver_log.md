# Frontend Version Log

`_docs/architecture.md` Part VI 규칙에 따른 프론트엔드 변경 이력. 커밋 전에 기록한다.

---

## [v1.0.0] - 2026-07-13

### Added

- `/plant`, `/plant/diagnosis/[id]`, `/plant/care-calendar` 페이지와
  `plant-photo-upload`, `plant-diagnosis-result-card`,
  `plant-care-calendar-list` 컴포넌트, `lib/plant-api.ts` 추가
- 홈(`/`)을 방구석 플랜트 매니저 랜딩으로 교체

### Removed

- gourmetmate 관련 라우트(`restaurants`, `admin`, `mypage`, `health-diet`,
  `couple-travel`, `onboarding`, `budget`, `food`) 및 연관 컴포넌트·lib 삭제
