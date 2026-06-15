from pydantic import BaseModel, Field


class FavoriteToggleRequest(BaseModel):
    store_id: int = Field(..., ge=1, description="카드·상세에 표시된 매장 id")

    model_config = {
        "json_schema_extra": {
            "example": {
                "store_id": 42,
            }
        }
    }


class FavoriteToggleResponse(BaseModel):
    store_id: int
    favorited: bool
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "store_id": 42,
                "favorited": True,
                "message": "즐겨찾기에 추가되었습니다.",
            }
        }
    }


class FavoriteCardItem(BaseModel):
    store_id: int
    restaurant_id: int
    name: str
    image_url: str = ""
    district: str = ""
    category_slug: str | None = None
    category_label: str | None = None
    signature_menu: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "store_id": 42,
                "restaurant_id": 42,
                "name": "스시 오마카세 강남",
                "image_url": "https://cdn.example.com/restaurants/42.jpg",
                "district": "강남구",
                "category_slug": "japanese",
                "category_label": "일식",
                "signature_menu": "오마카세 12종",
            }
        }
    }


class FavoriteCheckResponse(BaseModel):
    favorited_store_ids: list[int]

    model_config = {
        "json_schema_extra": {
            "example": {
                "favorited_store_ids": [42, 17, 88],
            }
        }
    }


from pydantic import BaseModel, Field


class FavoriteSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("즐겨찾기", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "즐겨찾기",
            }
        }
    }
