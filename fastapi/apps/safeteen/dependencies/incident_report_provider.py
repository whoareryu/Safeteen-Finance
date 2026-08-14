from __future__ import annotations

from safeteen.adapter.outbound.llm.gemini_incident_report_adapter import GeminiIncidentReportAdapter
from safeteen.app.ports.input.incident_report_use_case import IncidentReportUseCase
from safeteen.app.use_cases.incident_report_interactor import IncidentReportInteractor


def get_incident_report_use_case() -> IncidentReportUseCase:
    return IncidentReportInteractor(generator=GeminiIncidentReportAdapter())
