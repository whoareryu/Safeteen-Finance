-- GourmetMate DDL v2
-- 변경사항:
--   1. 1인당 추정 식대 → restaurants 병합 (역정규화)
--   2. 상세 연락처 → restaurants 병합 (역정규화)
--   3. AI 일일 맞춤 추천 User 복사 컬럼 제거
--   4. 즐겨찾기, 매장-태그 교차 테이블 복합 PK 적용
--   5. restaurant_view_stats 테이블 추가
--   6. 전체 컬럼 타입 실제화

-- ============================================================
-- 마스터 / 코드 테이블
-- ============================================================

CREATE TABLE food_categories (
    id              BIGSERIAL       PRIMARY KEY,
    slug            VARCHAR(50)     NOT NULL UNIQUE,
    label           VARCHAR(50)     NOT NULL
);

CREATE TABLE sigungu_districts (
    id              BIGSERIAL       PRIMARY KEY,
    sigungu_name    VARCHAR(50)     NOT NULL,
    district_label  VARCHAR(100)    NOT NULL
);

CREATE TABLE biz_classifications (
    id              BIGSERIAL       PRIMARY KEY,
    biz_mid_name    VARCHAR(100)    NOT NULL,
    biz_minor_name  VARCHAR(100)    NOT NULL,
    ksic_name       VARCHAR(100)    NOT NULL
);

CREATE TABLE tags (
    id              BIGSERIAL       PRIMARY KEY,
    slug            VARCHAR(50)     NOT NULL UNIQUE,
    label           VARCHAR(50)     NOT NULL
);

-- ============================================================
-- 핵심 엔티티
-- ============================================================

CREATE TABLE users (
    id              BIGSERIAL       PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL UNIQUE,
    email           VARCHAR(200)    NOT NULL UNIQUE,
    nickname        VARCHAR(50)     NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    role            VARCHAR(20)     NOT NULL DEFAULT 'user',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ
);

-- 역정규화: 1인당 추정 식대(avg_price), 상세 연락처(phone, place_url, source_note) 통합
CREATE TABLE restaurants (
    id                      BIGSERIAL       PRIMARY KEY,
    category_id             BIGINT          NOT NULL    REFERENCES food_categories(id),
    sigungu_id              BIGINT          NOT NULL    REFERENCES sigungu_districts(id),
    biz_classification_id   BIGINT          NOT NULL    REFERENCES biz_classifications(id),
    biz_number              VARCHAR(20)     NOT NULL,
    name                    VARCHAR(100)    NOT NULL,
    store_name              VARCHAR(100)    NOT NULL,
    branch_name             VARCHAR(50),
    road_address            VARCHAR(200)    NOT NULL,
    parcel_address          VARCHAR(200),
    latitude                DECIMAL(9,6)    NOT NULL,
    longitude               DECIMAL(9,6)    NOT NULL,
    description             TEXT,
    image_url               VARCHAR(500),
    view_count              INTEGER         NOT NULL DEFAULT 0,
    -- 역정규화: 1인당 추정 식대
    avg_price               NUMERIC(12,2),
    -- 역정규화: 상세 연락처
    phone                   VARCHAR(20),
    place_url               VARCHAR(500),
    source_note             VARCHAR(200)
);

-- ============================================================
-- 식당 1:N 자식 테이블
-- ============================================================

CREATE TABLE restaurant_menus (
    id              BIGSERIAL       PRIMARY KEY,
    restaurant_id   BIGINT          NOT NULL    REFERENCES restaurants(id) ON DELETE CASCADE,
    name            VARCHAR(100)    NOT NULL,
    is_signature    BOOLEAN         NOT NULL DEFAULT FALSE,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    unit_price      NUMERIC(12,2)   NOT NULL
);

CREATE TABLE restaurant_operating_hours (
    id              BIGSERIAL       PRIMARY KEY,
    restaurant_id   BIGINT          NOT NULL    REFERENCES restaurants(id) ON DELETE CASCADE,
    weekday         SMALLINT        NOT NULL CHECK (weekday BETWEEN 0 AND 6),  -- 0=월 ~ 6=일
    open_time       TIME,
    close_time      TIME,
    is_closed       BOOLEAN         NOT NULL DEFAULT FALSE,
    note            VARCHAR(200),
    UNIQUE (restaurant_id, weekday)
);

-- N:M 교차 테이블 — 복합 PK 적용
CREATE TABLE restaurant_tags (
    restaurant_id   BIGINT          NOT NULL    REFERENCES restaurants(id) ON DELETE CASCADE,
    tag_id          BIGINT          NOT NULL    REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (restaurant_id, tag_id)
);

-- ============================================================
-- 사용자 기능 테이블
-- ============================================================

-- 복합 PK 적용 (user당 restaurant 중복 불가)
CREATE TABLE favorites (
    user_id         BIGINT          NOT NULL    REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id   BIGINT          NOT NULL    REFERENCES restaurants(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, restaurant_id)
);

CREATE TABLE meal_plans (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         BIGINT          NOT NULL    REFERENCES users(id) ON DELETE CASCADE,
    monthly_budget  NUMERIC(12,2)   NOT NULL,
    spent_amount    NUMERIC(12,2)   NOT NULL DEFAULT 0,
    period_start    DATE            NOT NULL,
    period_end      DATE            NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- User 복사 컬럼 제거 — user_id/restaurant_id/meal_plan_id FK만 유지
CREATE TABLE daily_recommendations (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         BIGINT          NOT NULL    REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id   BIGINT          NOT NULL    REFERENCES restaurants(id),
    meal_plan_id    BIGINT                      REFERENCES meal_plans(id) ON DELETE SET NULL,
    recommended_on  DATE            NOT NULL,
    pick_reason     TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, recommended_on)  -- 하루 1곳 제약
);

-- ============================================================
-- 로그 / 통계 테이블
-- ============================================================

CREATE TABLE search_query_logs (
    id                  BIGSERIAL       PRIMARY KEY,
    query               VARCHAR(200)    NOT NULL,
    query_normalized    VARCHAR(200)    NOT NULL,
    result_count        INTEGER         NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ORM에만 존재하던 테이블 추가
CREATE TABLE restaurant_view_stats (
    id              BIGSERIAL       PRIMARY KEY,
    restaurant_id   BIGINT          NOT NULL    REFERENCES restaurants(id) ON DELETE CASCADE,
    user_id         BIGINT                      REFERENCES users(id) ON DELETE SET NULL,
    viewed_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 인덱스
-- ============================================================

CREATE INDEX idx_restaurants_category    ON restaurants(category_id);
CREATE INDEX idx_restaurants_sigungu     ON restaurants(sigungu_id);
CREATE INDEX idx_restaurants_location    ON restaurants(latitude, longitude);
CREATE INDEX idx_restaurants_avg_price   ON restaurants(avg_price);

CREATE INDEX idx_menus_restaurant        ON restaurant_menus(restaurant_id);
CREATE INDEX idx_hours_restaurant        ON restaurant_operating_hours(restaurant_id);

CREATE INDEX idx_favorites_user          ON favorites(user_id);
CREATE INDEX idx_favorites_restaurant    ON favorites(restaurant_id);

CREATE INDEX idx_meal_plans_user         ON meal_plans(user_id);
CREATE INDEX idx_daily_rec_user_date     ON daily_recommendations(user_id, recommended_on);

CREATE INDEX idx_view_stats_restaurant   ON restaurant_view_stats(restaurant_id);
CREATE INDEX idx_search_log_normalized   ON search_query_logs(query_normalized);
