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

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 42,
                "name": "스시 오마카세 강남",
                "image_url": "https://cdn.example.com/restaurants/42.jpg",
                "district": "강남구",
                "category_slug": "japanese",
                "category_label": "일식",
                "avg_price": 45000,
                "signature_menu": "오마카세 12종",
                "ai_tags": ["오마카세", "스시", "데이트"],
            }
        }
    }


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

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 42,
                "name": "스시 오마카세 강남",
                "category_slug": "japanese",
                "category_label": "일식",
                "district": "강남구",
                "description": "엄선한 재료로 만든 정통 오마카세 레스토랑",
                "avg_price": 45000,
                "road_address": "서울 강남구 도산대로 45길 12",
                "latitude": 37.5172,
                "longitude": 127.0473,
            }
        }
    }


class RestaurantCategoryListResponse(BaseModel):
    category_slug: str
    restaurants: list[RestaurantCardV2]
    offset: int
    limit: int
    total: int
    has_more: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "category_slug": "japanese",
                "offset": 0,
                "limit": 20,
                "total": 35,
                "has_more": True,
            }
        }
    }
