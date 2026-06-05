"""카탈로그·주제·주변·검색 제안·채팅·보강 API 스키마."""

from pydantic import BaseModel, Field

from gourmet.adapter.inbound.api.schemas.gourmet_schemas import (
    OffsetLimitPagination,
    RestaurantCardSummary,
)


class FoodCategoryItem(BaseModel):
    id: int
    slug: str
    label: str


class RestaurantMenuItem(BaseModel):
    id: int
    name: str
    is_signature: bool = False
    sort_order: int = 0
    unit_price: int | None = None


class RestaurantMenusResponse(BaseModel):
    restaurant_id: int
    menus: list[RestaurantMenuItem]
    signature_menu: str = ""


class TopicMetaBrief(BaseModel):
    slug: str
    title: str
    subtitle: str
    emoji: str
    keywords: list[str] = Field(default_factory=list)
    category_slugs: list[str] = Field(default_factory=list)


class TopicRestaurantsResponse(BaseModel):
    topic: TopicMetaBrief
    restaurants: list[RestaurantCardSummary]
    nearby_mode: bool = False
    pagination: OffsetLimitPagination


class NearbyRestaurantsResponse(BaseModel):
    latitude: float
    longitude: float
    radius_km: float
    restaurants: list[RestaurantCardSummary]
    pagination: OffsetLimitPagination


class SearchSuggestionItem(BaseModel):
    text: str
    source: str = Field(description="log | topic | chip")


class SearchSuggestResponse(BaseModel):
    query: str
    suggestions: list[SearchSuggestionItem]


class GourmetChatMessage(BaseModel):
    role: str = Field(..., description="user | assistant")
    content: str


class GourmetChatRequest(BaseModel):
    messages: list[GourmetChatMessage]
    restaurant_id: int | None = None
    q: str | None = Field(None, description="맛집 검색 맥락 키워드")
    model: str | None = None


class GourmetChatResponse(BaseModel):
    text: str
    model: str
    context_summary: str = ""


class EnrichmentSourceStatus(BaseModel):
    configured: bool
    note: str = ""


class RestaurantEnrichmentResponse(BaseModel):
    restaurant_id: int
    phone: str | None = None
    opening_hours: str | None = None
    closed_weekdays_label: str | None = None
    instagram_url: str | None = None
    extra_images: list[str] = Field(default_factory=list)
    sources: dict[str, EnrichmentSourceStatus] = Field(default_factory=dict)
    message: str = ""
