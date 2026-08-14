from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.app.dtos.incident_report_dto import IncidentReportResult


class IncidentReportGeneratorPort(ABC):
    """Outbound 출력 포트 — 피해 정황을 경찰 제출용 피해 경위서 초안으로 구성한다."""

    @abstractmethod
    async def generate(
        self, situation: str, image_bytes: bytes | None, image_content_type: str | None
    ) -> IncidentReportResult:
        pass
