from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.kerrigan_topology_dto import TopologyQuery, TopologyResponse


class KerriganTopologyUseCase(ABC):
    """Inbound 입력 포트 — 스타 토폴로지 레지스트리. 스포크 등록·조회."""

    @abstractmethod
    async def list_spokes(self, query: TopologyQuery) -> TopologyResponse:
        pass
