from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from plant.adapter.inbound.mappers.diagnosis_mapper import (
    to_detail_response,
    to_upload_response,
)
from plant.adapter.inbound.api.schemas.diagnosis_schema import (
    DiagnosisDetailResponse,
    DiagnosisUploadResponse,
)
from plant.app.dtos.diagnosis_dto import DiagnosisUploadCommand
from plant.app.ports.input.diagnosis_use_case import DiagnosisUseCase
from plant.dependencies.diagnosis_provider import get_diagnosis_use_case

diagnosis_router = APIRouter(prefix="/diagnosis", tags=["plant-diagnosis"])


@diagnosis_router.post("/upload", summary="잎사귀 사진 업로드 → 품종·증상 진단")
async def upload_diagnosis(
    file: UploadFile = File(...),
    region: str = Form(...),
    owner_user_id: int | None = Form(None),
    use_case: DiagnosisUseCase = Depends(get_diagnosis_use_case),
) -> DiagnosisUploadResponse:
    content = await file.read()
    command = DiagnosisUploadCommand(
        owner_user_id=owner_user_id,
        region=region,
        filename=file.filename or "unknown.jpg",
        content_type=file.content_type or "application/octet-stream",
        data=content,
    )
    result = await use_case.diagnose(command)
    return to_upload_response(result)


@diagnosis_router.get("/{diagnosis_id}", summary="진단 결과 조회")
async def get_diagnosis(
    diagnosis_id: int,
    use_case: DiagnosisUseCase = Depends(get_diagnosis_use_case),
) -> DiagnosisDetailResponse:
    result = await use_case.get(diagnosis_id)
    return to_detail_response(result)
