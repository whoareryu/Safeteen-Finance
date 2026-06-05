from pydantic import BaseModel, Field


class RestaurantCardV2(BaseModel):
    id: int
    name: str
    image_url: str = ""
    district: str = ""
    category_slug: str | None = None
    category_label: str | None = None
    avg_price: int | None = None
    signature_menu: str = ""
    ai_tags: list[str] = Field(default_factory=list)


class RestaurantDetailV2(BaseModel):
    id: int
    name: str
    category_slug: str
    category_label: str
    district: str
    description: str = ""
    image_url: str = ""
    avg_price: int | None = None
    signature_menu: str = ""
    ai_tags: list[str] = Field(default_factory=list)
    road_address: str = ""
    parcel_address: str = ""
    latitude: float | None = None
    longitude: float | None = None
    view_count: int = 0


class RestaurantCategoryListResponse(BaseModel):
    category_slug: str
    restaurants: list[RestaurantCardV2]
    offset: int
    limit: int
    total: int
    has_more: bool
