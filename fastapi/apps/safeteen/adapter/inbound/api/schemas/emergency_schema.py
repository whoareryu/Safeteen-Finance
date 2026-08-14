from __future__ import annotations

from pydantic import BaseModel


class EmergencyGuideRequest(BaseModel):
    situation: str | None = None


class EmergencyStepResponse(BaseModel):
    order: int
    title: str
    description: str


class EmergencyHotlineResponse(BaseModel):
    name: str
    phone_number: str
    description: str


class EmergencyGuideResponse(BaseModel):
    account_freeze_steps: list[EmergencyStepResponse]
    police_report_steps: list[EmergencyStepResponse]
    hotlines: list[EmergencyHotlineResponse]
