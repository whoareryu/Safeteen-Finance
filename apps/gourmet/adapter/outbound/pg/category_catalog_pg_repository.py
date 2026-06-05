from __future__ import annotations

from gourmet.app.ports.output.category_catalog_repository import CategoryCatalogRepository


class CategoryCatalogPgRepository(CategoryCatalogRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
