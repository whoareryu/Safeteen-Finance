from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmergencyGuideCommand:
    situation: str | None


@dataclass(frozen=True)
class EmergencyStepResult:
    order: int
    title: str
    description: str


@dataclass(frozen=True)
class EmergencyHotlineResult:
    name: str
    phone_number: str
    description: str


@dataclass(frozen=True)
class EmergencyGuideResult:
    account_freeze_steps: list[EmergencyStepResult]
    police_report_steps: list[EmergencyStepResult]
    hotlines: list[EmergencyHotlineResult]
