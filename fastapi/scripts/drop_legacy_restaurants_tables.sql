-- 기존 시드 전용 Gourmet 테이블 제거 후 ``restaurant``(공공 데이터) 단일 소스만 사용합니다.
-- PostgreSQL 에서 실행. 순서 준수 (FK).

BEGIN;

DROP TABLE IF EXISTS daily_picks CASCADE;
DROP TABLE IF EXISTS restaurant_view_stats CASCADE;
DROP TABLE IF EXISTS restaurants CASCADE;

COMMIT;
