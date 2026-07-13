from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CareGuideCommand:
    diagnosis_id: int


@dataclass(frozen=True)
class CareGuideResult:
    id: int
    diagnosis_record_id: int
    prescription_text: str
