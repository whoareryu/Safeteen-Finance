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

## [v1.1.0] - 2026-07-13

### Added

- soccer 앱 ORM 4종(stadium/team/schedule/player) + 마이그레이션 2개
  (create_soccer_schema, add_search_query_logs) 커밋. plant 마이그레이션
  (6b967960fd04)을 실제 DB 현재 상태(81c39ada7703) 위로 재배치
- PlantDoc 데이터셋을 `{species}__{symptom}` 분류 폴더로 변환해 로컬에서
  YOLO 분류 모델 학습 완료 (`apps/plant/resources/plant_yolo.pt`, top1 28.4%)
- `apps/soccer/_docs/soccer-dataset.sql`(원본), `soccer-dataset-inserts.sql`
  (CREATE TABLE 제거 + 컬럼명 보정된 실행용 INSERT) 추가

### Fixed

- `.gitignore`의 얼굴 인식 학습 이미지 제외 경로가 `apps/vision/...`로
  남아있던 걸 `apps/ontology/...`로 교정(vision→ontology 리네임 이후
  방치되어 이미지 118개가 실수로 git에 커밋되어 있었음 — untrack 처리),
  `apps/plant/resources/yolo_train/{train,val}/`도 추가로 제외

### Pending

- 실제 DB에 plant 마이그레이션 적용 및 soccer 데이터셋 INSERT는 원격
  서버(학원 PC) 재기동 후 진행 필요
