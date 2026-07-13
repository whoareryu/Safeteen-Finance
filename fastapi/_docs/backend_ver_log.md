# Backend Version Log

`_docs/architecture.md` Part VI 규칙에 따른 백엔드 변경 이력. 커밋 전에 기록한다.

---

## [v1.0.0] - 2026-07-13

### Added

- `apps/plant` 신규 앱 스캐폴딩 완료 (방구석 플랜트 매니저: photo-diagnosis,
  care-guide-generation, weather-monitoring, notification-scheduling)
- main.py에 plant_router 연결, `.importlinter`에 plant 스포크 등록

### Removed

- `apps/restaurant`, `apps/user`, `apps/gourmet_stub.py` 삭제 (gourmetmate 도메인 → plant로 전환)
