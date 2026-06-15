"""Gourmet API 요청·응답 스키마 (Pydantic) — FastAPI 라우터에서 사용."""

from pydantic import BaseModel, Field


class TopicBrowsePagination(BaseModel):
    """홈·카테고리 주제 행 — 주제(행) 단위 윈도우."""

    topic_offset: int = Field(..., ge=0, description="필터된 주제 목록 기준 시작 인덱스")
    topic_limit: int = Field(..., ge=1, description="이번 요청에 포함할 최대 주제(행) 수")
    total_topics: int = Field(..., ge=0, description="검색·필터 후 주제 총 개수")
    per_topic_limit: int = Field(..., ge=1, description="행당 맛집 카드 최대 개수")
    has_more: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "topic_offset": 0,
                "topic_limit": 4,
                "total_topics": 18,
                "per_topic_limit": 10,
                "has_more": True,
            }
        }
    }


class OffsetLimitPagination(BaseModel):
    """검색·오늘의 맛집 등 — 일렬 목록 offset/limit."""

    offset: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    total: int = Field(..., ge=0, description="페이지네이션 전 전체 매칭 수")
    has_more: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "offset": 0,
                "limit": 20,
                "total": 42,
                "has_more": True,
            }
        }
    }


class RestaurantCardSummary(BaseModel):
    """목록·카드용 — 이름·사진·한 줄 위치. 상세는 ``GET /restaurants/{id}``."""

    id: int
    name: str
    image_url: str
    district: str = ""
    distance_km: float | None = None
    rank: int | None = None
    category_slug: str | None = None
    category_label: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 42,
                "name": "스시 오마카세 강남",
                "image_url": "https://cdn.example.com/restaurants/42.jpg",
                "district": "강남구",
                "category_slug": "japanese",
                "category_label": "일식",
            }
        }
    }


class TodayPickItem(BaseModel):
    """레거시·시드 호환. 목록 API는 ``RestaurantCardSummary`` 사용."""

    rank: int
    id: int
    name: str
    category_slug: str
    category_label: str
    district: str
    description: str
    image_url: str
    view_count: int = 0
    distance_km: float | None = None
    detail_href: str | None = Field(
        default=None,
        description="시드 레스토랑 외 카드 연결 경로 (예: `/stores/official/{id}`).",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "rank": 1,
                "id": 42,
                "name": "스시 오마카세 강남",
                "category_slug": "japanese",
                "category_label": "일식",
                "district": "강남구",
                "description": "엄선한 재료로 만든 정통 오마카세",
                "image_url": "https://cdn.example.com/restaurants/42.jpg",
            }
        }
    }


class RestaurantViewStatResponse(BaseModel):
    restaurant_id: int
    restaurant_name: str
    view_count: int
    first_viewed_at: str | None
    last_viewed_at: str | None

    model_config = {
        "json_schema_extra": {
            "example": {
                "restaurant_id": 42,
                "restaurant_name": "스시 오마카세 강남",
                "view_count": 0,
                "first_viewed_at": None,
                "last_viewed_at": None,
            }
        }
    }


class RecordViewResponse(BaseModel):
    restaurant_id: int
    view_count: int
    message: str = "조회가 기록되었습니다."

    model_config = {
        "json_schema_extra": {
            "example": {
                "restaurant_id": 42,
                "view_count": 0,
                "message": "조회가 기록되었습니다.",
            }
        }
    }


class MenuItemResponse(BaseModel):
    name: str
    price: int
    note: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "오마카세 12종",
                "price": 85000,
                "note": "제철 재료 사용",
            }
        }
    }


class RestaurantDetailResponse(BaseModel):
    id: int
    name: str
    category_slug: str
    category_label: str
    district: str
    description: str
    image_url: str
    view_count: int = 0
    closed_weekdays: list[int] = []
    closed_weekdays_label: str = ""
    address: str = ""
    opening_hours: str = ""
    phone: str | None = None
    instagram_url: str | None = None
    reservation_available: bool = False
    reservation_note: str = ""
    menu_items: list[MenuItemResponse] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 42,
                "name": "스시 오마카세 강남",
                "category_slug": "japanese",
                "category_label": "일식",
                "district": "강남구",
                "description": "엄선한 재료로 만든 정통 오마카세 레스토랑",
                "image_url": "https://cdn.example.com/restaurants/42.jpg",
                "address": "서울 강남구 도산대로 45길 12",
                "opening_hours": "화~일 12:00–22:00",
            }
        }
    }


WEEKDAY_KO = ("월", "화", "수", "목", "금", "토", "일")


def format_closed_weekdays_label(closed: list[int]) -> str:
    if not closed:
        return "연중무휴 (휴무 정보 없음)"
    days = [WEEKDAY_KO[d] for d in sorted(closed) if 0 <= d <= 6]
    return f"매주 {', '.join(days)}요일 휴무"


class TodayPicksResponse(BaseModel):
    title: str = "오늘의 맛집"
    date: str
    picks_per_category_min: int = 2
    picks_per_category_max: int = 3
    picks: list[RestaurantCardSummary]
    nearby_mode: bool = False
    pagination: OffsetLimitPagination

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "오늘의 맛집",
                "date": "2026-06-15",
                "nearby_mode": False,
            }
        }
    }


class TopicMeta(BaseModel):
    slug: str
    title: str
    subtitle: str
    emoji: str
    keywords: list[str] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "slug": "sushi-omakase",
                "title": "오마카세 맛집",
                "subtitle": "셰프가 직접 고른 제철 스시",
                "emoji": "🍣",
                "keywords": ["오마카세", "스시", "고급"],
            }
        }
    }


class TopicRowResponse(BaseModel):
    slug: str
    title: str
    subtitle: str
    emoji: str
    keywords: list[str] = []
    restaurants: list[RestaurantCardSummary]
    category_slug: str | None = None
    category_label: str | None = None
    link_title: bool = Field(
        default=True,
        description="False면 행 제목을 주제(`/topics/...`)에 연결하지 않음.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "slug": "sushi-omakase",
                "title": "오마카세 맛집",
                "subtitle": "셰프가 직접 고른 제철 스시",
                "emoji": "🍣",
                "category_slug": "japanese",
                "category_label": "일식",
            }
        }
    }


class HomeBrowseResponse(BaseModel):
    query: str | None = None
    topic_count: int
    topics: list[TopicRowResponse]
    nearby_mode: bool = False
    pagination: TopicBrowsePagination

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": None,
                "topic_count": 8,
                "nearby_mode": False,
            }
        }
    }


class SearchMatchedTopic(BaseModel):
    slug: str
    title: str
    emoji: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "slug": "sushi-omakase",
                "title": "오마카세 맛집",
                "emoji": "🍣",
            }
        }
    }


class RestaurantSearchResponse(BaseModel):
    query: str
    summary: str
    matched_topics: list[SearchMatchedTopic] = []
    restaurants: list[RestaurantCardSummary]
    nearby_mode: bool = False
    pagination: OffsetLimitPagination

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "스시",
                "summary": "스시 관련 맛집 12곳을 찾았습니다",
                "nearby_mode": False,
            }
        }
    }


class CategoryBrowseResponse(BaseModel):
    category_slug: str
    category_label: str
    query: str | None = None
    topic_count: int
    topics: list[TopicRowResponse]
    nearby_mode: bool = False
    pagination: TopicBrowsePagination

    model_config = {
        "json_schema_extra": {
            "example": {
                "category_slug": "japanese",
                "category_label": "일식",
                "topic_count": 6,
                "nearby_mode": False,
            }
        }
    }
