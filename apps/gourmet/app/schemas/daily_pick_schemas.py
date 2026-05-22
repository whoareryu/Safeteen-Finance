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


class DailyPickResponse(BaseModel):
    date: str
    restaurant: DailyPickRestaurantCard | None
    daily_budget: int | None = Field(
        None, description="버짓설정 시 하루 권장 식비(원) = 기간 목표 ÷ 기간 일수"
    )
    budget_applied: bool = False
    message: str = ""
