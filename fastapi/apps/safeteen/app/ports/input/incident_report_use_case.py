from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.app.dtos.incident_report_dto import IncidentReportCommand, IncidentReportResult


class IncidentReportUseCase(ABC):
    """Inbound 입력 포트 — 피해 경위서 및 증거 제출 서식 자동 작성."""

    @abstractmethod
    async def generate(self, command: IncidentReportCommand) -> IncidentReportResult:
        pass
