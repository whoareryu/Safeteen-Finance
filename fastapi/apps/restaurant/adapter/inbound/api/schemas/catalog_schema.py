"""카탈로그·주제·주변·검색 제안·채팅·보강 API 스키마."""

from pydantic import BaseModel, Field

from restaurant.adapter.inbound.api.schemas.gourmet_schema import (
    OffsetLimitPagination,
    RestaurantCardSummary,
)


class FoodCategoryItem(BaseModel):
    id: int
    slug: str
    label: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 3,
                "slug": "japanese",
                "label": "일식",
            }
        }
    }


class RestaurantMenuItem(BaseModel):
    id: int
    name: str
    is_signature: bool = False
    sort_order: int = 0
    unit_price: int | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 7,
                "name": "오마카세 12종",
                "is_signature": True,
                "sort_order": 1,
                "unit_price": 85000,
            }
        }
    }


class RestaurantMenusResponse(BaseModel):
    restaurant_id: int
    menus: list[RestaurantMenuItem]
    signature_menu: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "restaurant_id": 42,
                "signature_menu": "오마카세 12종",
            }
        }
    }


class TopicMetaBrief(BaseModel):
    slug: str
    title: str
    subtitle: str
    emoji: str
    keywords: list[str] = Field(default_factory=list)
    category_slugs: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "slug": "sushi-omakase",
                "title": "오마카세 맛집",
                "subtitle": "셰프가 직접 고른 제철 스시",
                "emoji": "🍣",
                "keywords": ["오마카세", "스시"],
                "category_slugs": ["japanese"],
            }
        }
    }


class TopicRestaurantsResponse(BaseModel):
    topic: TopicMetaBrief
    restaurants: list[RestaurantCardSummary]
    nearby_mode: bool = False
    pagination: OffsetLimitPagination

    model_config = {
        "json_schema_extra": {
            "example": {
                "nearby_mode": False,
            }
        }
    }


class NearbyRestaurantsResponse(BaseModel):
    latitude: float
    longitude: float
    radius_km: float
    restaurants: list[RestaurantCardSummary]
    pagination: OffsetLimitPagination

    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": 37.5172,
                "longitude": 127.0473,
                "radius_km": 1.0,
            }
        }
    }


class SearchSuggestionItem(BaseModel):
    text: str
    source: str = Field(description="log | topic | chip")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "오마카세",
                "source": "topic",
            }
        }
    }


class SearchSuggestResponse(BaseModel):
    query: str
    suggestions: list[SearchSuggestionItem]

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "오마",
            }
        }
    }


class GourmetChatMessage(BaseModel):
    role: str = Field(..., description="user | assistant")
    content: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "user",
                "content": "강남에서 분위기 좋은 일식집 추천해줘",
            }
        }
    }


class GourmetChatRequest(BaseModel):
    messages: list[GourmetChatMessage]
    restaurant_id: int | None = None
    q: str | None = Field(None, description="맛집 검색 맥락 키워드")
    model: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "restaurant_id": None,
                "q": "강남 일식",
                "model": None,
            }
        }
    }


class GourmetChatResponse(BaseModel):
    text: str
    model: str
    context_summary: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "강남에서 분위기 좋은 일식집으로 '스시 오마카세 강남'을 추천드립니다.",
                "model": "gemini-1.5-flash",
                "context_summary": "강남 일식 추천",
            }
        }
    }


class EnrichmentSourceStatus(BaseModel):
    configured: bool
    note: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "configured": True,
                "note": "Kakao 로컬 API 연결됨",
            }
        }
    }


class RestaurantEnrichmentResponse(BaseModel):
    restaurant_id: int
    phone: str | None = None
    opening_hours: str | None = None
    closed_weekdays_label: str | None = None
    instagram_url: str | None = None
    extra_images: list[str] = Field(default_factory=list)
    sources: dict[str, EnrichmentSourceStatus] = Field(default_factory=dict)
    message: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "restaurant_id": 42,
                "phone": "02-1234-5678",
                "opening_hours": "화~일 12:00–22:00",
                "closed_weekdays_label": "매주 월요일 휴무",
                "message": "정보 보강 완료",
            }
        }
    }
