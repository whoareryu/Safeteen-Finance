from fastapi import APIRouter

from star_craft.adapter.inbound.api.v1.kerrigan_topology_router import kerrigan_topology_router
from star_craft.adapter.inbound.api.v1.zeratul_context_router import zeratul_context_router
from star_craft.adapter.inbound.api.v1.artanis_graph_router import artanis_graph_router

star_craft_router = APIRouter(prefix="/star-craft", tags=["star-craft"])
star_craft_router.include_router(kerrigan_topology_router)
star_craft_router.include_router(zeratul_context_router)
star_craft_router.include_router(artanis_graph_router)

__all__ = [
    "star_craft_router",
    "kerrigan_topology_router",
    "zeratul_context_router",
    "artanis_graph_router",
]
