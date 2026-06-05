from datetime import date

from pydantic import BaseModel, Field

from gourmet.adapter.inbound.api.schemas.restaurant_schemas import RestaurantCardV2


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    monthly_budget: int
    spent_amount: int
    period_start: date
    period_end: date
    remaining_budget: int


class MealPlanUpsertRequest(BaseModel):
    monthly_budget: int = Field(..., ge=0, description="한 달 목표 식비(원)")
    spent_amount: int = Field(0, ge=0, description="현재까지 지출(원)")
    period_start: date
    period_end: date


class MealPlanRestaurantsResponse(BaseModel):
    plan: MealPlanResponse | None
    per_meal_cap: int = Field(..., description="이번 조회 기준 1끼 추정 상한(원)")
    restaurants: list[RestaurantCardV2]
    offset: int
    limit: int
