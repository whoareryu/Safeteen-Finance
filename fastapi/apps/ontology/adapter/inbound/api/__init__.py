from fastapi import APIRouter

from ontology.adapter.inbound.api.v1.sommelier_graph_router import sommelier_graph_router
from ontology.adapter.inbound.api.v1.lens_search_router import lens_search_router
from ontology.adapter.inbound.api.v1.maestro_router import maestro_router
from ontology.adapter.inbound.api.v1.gemini_router import gemini_router
from ontology.adapter.inbound.api.v1.semantic_routing_router import semantic_routing_router
from ontology.adapter.inbound.api.v1.crawler_router import crawler_router
from ontology.adapter.inbound.api.v1.scraper_router import scraper_router

ontology_router = APIRouter(prefix="/ontology", tags=["ontology"])
ontology_router.include_router(sommelier_graph_router)
ontology_router.include_router(lens_search_router)
ontology_router.include_router(maestro_router)
ontology_router.include_router(gemini_router)
ontology_router.include_router(semantic_routing_router)
ontology_router.include_router(crawler_router)
ontology_router.include_router(scraper_router)

__all__ = [
    "ontology_router",
    "sommelier_graph_router",
    "lens_search_router",
    "maestro_router",
    "gemini_router",
    "semantic_routing_router",
    "crawler_router",
    "scraper_router",
]
