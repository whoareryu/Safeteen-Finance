"""하위 호환 re-export — 신규 코드는 gourmet.app.ports.output 을 사용."""

from user.app.ports.output.meal_plan_repository import IMealPlanRepository
from restaurant.app.ports.output.restaurant_repository import IRestaurantRepository

__all__ = ["IRestaurantRepository", "IMealPlanRepository"]
