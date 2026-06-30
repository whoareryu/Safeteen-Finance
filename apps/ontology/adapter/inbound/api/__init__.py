from fastapi import APIRouter

from ontology.adapter.inbound.api.v1.sommelier_graph_router import sommelier_graph_router
from ontology.adapter.inbound.api.v1.lens_search_router import lens_search_router
from ontology.adapter.inbound.api.v1.maestro_router import maestro_router

ontology_router = APIRouter(prefix="/ontology", tags=["ontology"])
ontology_router.include_router(sommelier_graph_router)
ontology_router.include_router(lens_search_router)
ontology_router.include_router(maestro_router)

__all__ = [
    "ontology_router",
    "sommelier_graph_router",
    "lens_search_router",
    "maestro_router",
]
