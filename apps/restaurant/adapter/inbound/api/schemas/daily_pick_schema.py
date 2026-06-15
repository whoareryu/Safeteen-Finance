from pydantic import BaseModel, Field


class DailyPickRestaurantCard(BaseModel):
    id: int
    name: str
    image_url: str = ""
    district: str = ""
    category_slug: str | None = None
    category_label: str | None = None
    avg_price: int | None = None
    signature_menu: str = ""
    distance_km: float | None = None

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
            }
        }
    }


class DailyPickResponse(BaseModel):
    date: str
    restaurant: DailyPickRestaurantCard | None
    daily_budget: int | None = Field(
        None, description="버짓설정 시 하루 권장 식비(원) = 기간 목표 ÷ 기간 일수"
    )
    budget_applied: bool = False
    message: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2026-06-15",
                "daily_budget": 15000,
                "budget_applied": True,
                "message": "오늘의 추천 맛집입니다",
            }
        }
    }


class DailyPickSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("오늘의 맛집 추천", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "오늘의 맛집 추천",
            }
        }
    }
