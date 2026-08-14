from __future__ import annotations

from safeteen.app.dtos.incident_report_dto import IncidentReportCommand, IncidentReportResult
from safeteen.app.ports.input.incident_report_use_case import IncidentReportUseCase
from safeteen.app.ports.output.incident_report_generator_port import IncidentReportGeneratorPort


class IncidentReportInteractor(IncidentReportUseCase):

    def __init__(self, generator: IncidentReportGeneratorPort) -> None:
        self._generator = generator

    async def generate(self, command: IncidentReportCommand) -> IncidentReportResult:
        if not command.situation or not command.situation.strip():
            raise ValueError("피해 정황(situation)은 필수입니다.")

        return await self._generator.generate(
            command.situation, command.image_bytes, command.image_content_type
        )
