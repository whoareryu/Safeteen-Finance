from functools import lru_cache

from restaurant.adapter.outbound.pg.topic_restaurants_pg_repository import TopicRestaurantsPgRepository
from restaurant.app.ports.input.topic_restaurants_use_case import TopicRestaurantsUseCase
from restaurant.app.ports.output.topic_restaurants_repository import TopicRestaurantsRepository
from restaurant.app.use_cases.topic_restaurants_interactor import TopicRestaurantsInteractor


@lru_cache
def get_topic_restaurants_use_case() -> TopicRestaurantsUseCase:
    repository: TopicRestaurantsRepository = TopicRestaurantsPgRepository()
    return TopicRestaurantsInteractor(repository=repository)
