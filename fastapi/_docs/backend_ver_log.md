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

## [v1.2.0] - 2026-07-14

### Added

- `apps/plant`에 신규 feature slice `knowledge-ingestion` 추가: 농사로
  (건조에 강한 식물/실내정원용 식물) + 공공데이터포털(공기정화식물) 3개
  API 클라이언트, `KnowledgeSyncInteractor`(`POST /api/plant/knowledge/sync`)가
  정규화된 `PlantKnowledgeFact`를 ontology 허브의 기존
  `SommelierUseCase.query()`(MERGE Cypher)로 Neo4j `Species` 노드에 적재
  (신규 write 포트를 따로 만들지 않고 이미 존재하는 범용 Cypher 실행
  포트를 재사용 — 단순성 우선)
- `care_guide_interactor.py`의 Sommelier 조회 쿼리를
  `(Species)-[:HAS_SYMPTOM]->(Disease)` 고정 스키마에서 `Species` 이름
  부분일치 매칭 + `RETURN s`(속성 전체)로 변경 — 실제 적재되는 한국어
  품종명과 YOLO 진단 라벨을 느슨하게 매칭하기 위함

### Fixed

- `daily_picks`/`restaurant_view_stats` 고아 테이블(FK 대상 `restaurants`가
  이미 CASCADE로 삭제되어 참조 무결성 없이 남아있던 테이블) 정리 마이그레이션
  (`c9d122a45661`) 작성 및 실제 DB 적용 완료

### Pending

- 공기정화식물 API(`NihhsFuriAirInfo`) 키가 승인 직후 활성화 대기 상태(401
  Unauthorized) — 활성화 후 재검증 필요. 파서는 활용가이드 문서 스펙
  기반으로 작성했을 뿐 실응답으로 검증되지 않음
- `knowledge_sync_router`는 원격 배포(코드 push + 컨테이너 재생성으로
  신규 env 반영) 후 실키 기반 Neo4j 적재까지 종단 검증 필요 — 이번엔
  로컬에서 농사로 2개 클라이언트의 실 API 호출까지만 검증함
