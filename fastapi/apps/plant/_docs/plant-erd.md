# Plant Manager ERD

`apps/plant` 관계형 스키마(PostgreSQL) ERD. ORM 정의(`apps/plant/adapter/outbound/orm/*.py`) 기준.

```mermaid
erDiagram
    plants ||--o{ diagnosis_records : "1개 식물 : N개 진단 (plant_id)"
    plants ||--o{ care_schedules : "1개 식물 : N개 관리 스케줄 (plant_id)"
    plants ||--o{ notification_events : "1개 식물 : N개 알림 (plant_id, nullable)"
    diagnosis_records ||--o{ care_prescriptions : "1개 진단 : N개 처방 (diagnosis_record_id)"

    plants {
        int id PK
        int owner_user_id "FK 제약 없음 — users.id 참조 의도"
        string nickname
        string species_name
        string region "weather_snapshots.region과 소프트 조인"
        datetime created_at
    }

    diagnosis_records {
        int id PK
        int plant_id FK
        string photo_url
        string detected_species
        float species_confidence
        string symptom_label
        float symptom_confidence
        datetime diagnosed_at
    }

    care_prescriptions {
        int id PK
        int diagnosis_record_id FK
        text prescription_text
        string llm_model
        datetime generated_at
    }

    care_schedules {
        int id PK
        int plant_id FK
        int interval_days
        datetime last_watered_at
        datetime next_watering_due_at
        string status "default: active"
    }

    notification_events {
        int id PK
        int plant_id FK "nullable"
        string channel
        text message
        string coupang_link
        string triggered_by
        string delivery_status "default: pending"
        datetime sent_at
    }

    weather_snapshots {
        int id PK
        string region "FK 아님 — plants.region과 문자열 매칭"
        float temp_c
        float humidity_pct
        string sunlight_desc
        bool is_dry_day
        datetime recorded_at
    }
```

## 테이블 요약

| 테이블 | PK | FK (실제 제약) | 비고 |
|--------|----|--------|------|
| `plants` | `id` | — | `owner_user_id`는 FK 제약 없이 `apps/auth` 쪽 `users.id` 값을 참조하는 용도. `region`은 `weather_snapshots.region`과 문자열로만 연결(FK 아님) |
| `diagnosis_records` | `id` | `plant_id` → `plants.id` | 사진 기반 종·병징 진단 결과 (species/symptom confidence 포함) |
| `care_prescriptions` | `id` | `diagnosis_record_id` → `diagnosis_records.id` | 진단 결과 기반 LLM 처방 텍스트, `llm_model` 컬럼에 사용 모델명 기록 |
| `care_schedules` | `id` | `plant_id` → `plants.id` | 급수 등 관리 주기(`interval_days`) 및 다음 예정일 |
| `notification_events` | `id` | `plant_id` → `plants.id` (nullable) | 알림 발송 이력 — `coupang_link`로 커머스 연계, `delivery_status`로 발송 상태 추적 |
| `weather_snapshots` | `id` | — | 지역별 날씨 스냅샷. 다른 테이블과 FK로 연결되지 않고 `region` 문자열로만 매칭 |

## 참고

- ORM 소스: `apps/plant/adapter/outbound/orm/{plant,diagnosis_record,care_prescription,care_schedule,notification_event,weather_snapshot}_orm.py`
- 모든 PK는 `IntIdPrimaryKeyMixin` (`id`, autoincrement) 공통 사용
- 이 ERD는 **관계형(PostgreSQL) 스키마**만 다룬다. 외부 식물 데이터 API → Neo4j 지식그래프 적재 파이프라인(품종·생태 정보 그래프)은 별도 그래프 모델이며 이 문서 범위 밖.
