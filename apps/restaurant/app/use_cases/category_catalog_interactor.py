"""``food_categories`` 마스터 조회."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.pg.food_category_pg_repository import FoodCategoryRepository
from restaurant.app.ports.input.category_catalog_use_case import CategoryCatalogUseCase
from restaurant.adapter.inbound.api.schemas.category_catalog_schema import CategoryCatalogSchema
from restaurant.app.dtos.category_catalog_dto import CategoryCatalogQuery, CategoryCatalogResponse
from restaurant.app.ports.output.category_catalog_repository import CategoryCatalogRepository


def list_food_categories(db: Session) -> list[dict]:
    FoodCategoryRepository().ensure_seeded(db)
    rows = db.scalars(select(FoodCategory).order_by(FoodCategory.id)).all()
    return [{"id": c.id, "slug": c.slug, "label": c.label} for c in rows]


class CategoryCatalogInteractor(CategoryCatalogUseCase):
    def __init__(self, repository: CategoryCatalogRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: CategoryCatalogSchema) -> CategoryCatalogResponse:
        return await self.repository.introduce_myself(
            CategoryCatalogQuery(id=schema.id, name=schema.name)
        )
