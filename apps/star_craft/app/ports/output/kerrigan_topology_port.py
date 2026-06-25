from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.kerrigan_topology_dto import TopologyQuery, TopologyResponse


class KerriganTopologyPort(ABC):

    @abstractmethod
    async def list_spokes(self, query: TopologyQuery) -> TopologyResponse:
        pass
