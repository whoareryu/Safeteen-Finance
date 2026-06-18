from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse


class HartleyViolinUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/hartley_violin_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: HartleyViolinQuery) -> HartleyViolinResponse:
        """Hartley 바이올린을 조회한다."""
        pass

    @abstractmethod
    def get_correlation_heatmap(self, df: pd.DataFrame) -> bytes:
        """상관관계 히트맵 PNG 이미지 바이트를 반환한다."""
        pass

    @abstractmethod
    def get_correlation_chart(self, df: pd.DataFrame) -> dict:
        """Plotly 인터랙티브 상관관계 차트 JSON을 반환한다."""
        pass
