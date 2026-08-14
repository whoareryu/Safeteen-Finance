from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IncidentReportCommand:
    situation: str
    image_bytes: bytes | None
    image_content_type: str | None


@dataclass(frozen=True)
class IncidentReportResult:
    incident_summary: str
    victim_statement: str
    evidence_list: list[str]
    requested_action: str
