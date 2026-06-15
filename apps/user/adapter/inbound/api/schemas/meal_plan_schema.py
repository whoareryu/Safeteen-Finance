from datetime import date

from pydantic import BaseModel, Field

from restaurant.adapter.inbound.api.schemas.restaurant_schema import RestaurantCardV2


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    monthly_budget: int
    spent_amount: int
    period_start: date
    period_end: date
    remaining_budget: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 7,
                "monthly_budget": 300000,
                "spent_amount": 45000,
                "period_start": "2026-06-01",
                "period_end": "2026-06-30",
                "remaining_budget": 255000,
            }
        }
    }


class MealPlanUpsertRequest(BaseModel):
    monthly_budget: int = Field(..., ge=0, description="한 달 목표 식비(원)")
    spent_amount: int = Field(0, ge=0, description="현재까지 지출(원)")
    period_start: date
    period_end: date

    model_config = {
        "json_schema_extra": {
            "example": {
                "monthly_budget": 300000,
                "spent_amount": 0,
                "period_start": "2026-06-01",
                "period_end": "2026-06-30",
            }
        }
    }


class MealPlanRestaurantsResponse(BaseModel):
    plan: MealPlanResponse | None
    per_meal_cap: int = Field(..., description="이번 조회 기준 1끼 추정 상한(원)")
    restaurants: list[RestaurantCardV2]
    offset: int
    limit: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "per_meal_cap": 12500,
                "offset": 0,
                "limit": 20,
            }
        }
    }


from pydantic import BaseModel, Field


class MealPlanSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("식비 계획", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "식비 계획",
            }
        }
    }
