# GourmetMate ERD v2

역정규화 적용 내역:
- `1인당 추정 식대` → `restaurants`에 `avg_price` 컬럼으로 병합
- `상세 연락처` → `restaurants`에 `phone`, `place_url`, `source_note` 컬럼으로 병합
- `AI 일일 맞춤 추천`에서 User 복사 컬럼 제거, FK만 유지
- `즐겨찾기 / 찜`의 PK를 복합 PK(user_id + restaurant_id)로 변경
- `매장-태그 연결 교차`의 PK를 복합 PK(restaurant_id + tag_id)로 변경
- `restaurant_view_stats` 테이블 추가 (ORM 누락분 반영)
- 전체 컬럼 타입을 실제 의미에 맞게 수정

```mermaid
erDiagram
    users {
        BIGINT id PK
        VARCHAR_50 username
        VARCHAR_200 email
        VARCHAR_50 nickname
        VARCHAR_255 password_hash
        VARCHAR_20 role
        TIMESTAMPTZ created_at
        TIMESTAMPTZ last_login_at
    }

    food_categories {
        BIGINT id PK
        VARCHAR_50 slug
        VARCHAR_50 label
    }

    sigungu_districts {
        BIGINT id PK
        VARCHAR_50 sigungu_name
        VARCHAR_100 district_label
    }

    biz_classifications {
        BIGINT id PK
        VARCHAR_100 biz_mid_name
        VARCHAR_100 biz_minor_name
        VARCHAR_100 ksic_name
    }

    restaurants {
        BIGINT id PK
        BIGINT category_id FK
        BIGINT sigungu_id FK
        BIGINT biz_classification_id FK
        VARCHAR_20 biz_number
        VARCHAR_100 name
        VARCHAR_100 store_name
        VARCHAR_50 branch_name
        VARCHAR_200 road_address
        VARCHAR_200 parcel_address
        DECIMAL_9_6 latitude
        DECIMAL_9_6 longitude
        TEXT description
        VARCHAR_500 image_url
        INTEGER view_count
        NUMERIC_12_2 avg_price "역정규화: 1인당 추정 식대"
        VARCHAR_20 phone "역정규화: 상세 연락처"
        VARCHAR_500 place_url "역정규화: 상세 연락처"
        VARCHAR_200 source_note "역정규화: 상세 연락처"
    }

    tags {
        BIGINT id PK
        VARCHAR_50 slug
        VARCHAR_50 label
    }

    restaurant_tags {
        BIGINT restaurant_id PK
        BIGINT tag_id PK
    }

    restaurant_menus {
        BIGINT id PK
        BIGINT restaurant_id FK
        VARCHAR_100 name
        BOOLEAN is_signature
        INTEGER sort_order
        NUMERIC_12_2 unit_price
    }

    restaurant_operating_hours {
        BIGINT id PK
        BIGINT restaurant_id FK
        SMALLINT weekday "0=월 ~ 6=일"
        TIME open_time
        TIME close_time
        BOOLEAN is_closed
        VARCHAR_200 note
    }

    meal_plans {
        BIGINT id PK
        BIGINT user_id FK
        NUMERIC_12_2 monthly_budget
        NUMERIC_12_2 spent_amount
        DATE period_start
        DATE period_end
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    favorites {
        BIGINT user_id PK
        BIGINT restaurant_id PK
        TIMESTAMPTZ created_at
    }

    daily_recommendations {
        BIGINT id PK
        BIGINT user_id FK
        BIGINT restaurant_id FK
        BIGINT meal_plan_id FK
        DATE recommended_on
        TEXT pick_reason
        TIMESTAMPTZ created_at
    }

    search_query_logs {
        BIGINT id PK
        VARCHAR_200 query
        VARCHAR_200 query_normalized
        INTEGER result_count
        TIMESTAMPTZ created_at
    }

    restaurant_view_stats {
        BIGINT id PK
        BIGINT restaurant_id FK
        BIGINT user_id FK
        TIMESTAMPTZ viewed_at
    }

    users ||--o{ meal_plans : "has"
    users ||--o{ favorites : "saves"
    users ||--o{ daily_recommendations : "receives"
    users ||--o{ restaurant_view_stats : "views"

    food_categories ||--o{ restaurants : "classifies"
    sigungu_districts ||--o{ restaurants : "locates"
    biz_classifications ||--o{ restaurants : "categorizes"

    restaurants ||--o{ restaurant_menus : "has"
    restaurants ||--o{ restaurant_operating_hours : "has"
    restaurants ||--o{ restaurant_tags : "tagged_with"
    restaurants ||--o{ favorites : "saved_by"
    restaurants ||--o{ daily_recommendations : "recommended_in"
    restaurants ||--o{ restaurant_view_stats : "tracked_by"

    tags ||--o{ restaurant_tags : "applied_to"

    meal_plans ||--o{ daily_recommendations : "used_in"
```

---

## 관련 문서

[[whoareryu/_claude/CLAUDE\|Backend CLAUDE]] · [[GOURMET_ERD]] · [[ENTITY_RULE]] · [[EXTERNAL_API_KEYS]]
