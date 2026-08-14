from __future__ import annotations

from safeteen.adapter.inbound.api.schemas.incident_report_schema import IncidentReportResponse
from safeteen.app.dtos.incident_report_dto import IncidentReportResult


def to_response(result: IncidentReportResult) -> IncidentReportResponse:
    return IncidentReportResponse(
        incident_summary=result.incident_summary,
        victim_statement=result.victim_statement,
        evidence_list=result.evidence_list,
        requested_action=result.requested_action,
    )
