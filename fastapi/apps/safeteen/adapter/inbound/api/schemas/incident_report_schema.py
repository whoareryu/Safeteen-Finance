from __future__ import annotations

from pydantic import BaseModel


class IncidentReportResponse(BaseModel):
    incident_summary: str
    victim_statement: str
    evidence_list: list[str]
    requested_action: str
