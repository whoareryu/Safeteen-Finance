from __future__ import annotations

import mimetypes

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from safeteen.adapter.inbound.api.schemas.incident_report_schema import IncidentReportResponse
from safeteen.adapter.inbound.mappers.incident_report_mapper import to_response
from safeteen.app.dtos.incident_report_dto import IncidentReportCommand
from safeteen.app.ports.input.incident_report_use_case import IncidentReportUseCase
from safeteen.dependencies.incident_report_provider import get_incident_report_use_case

incident_report_router = APIRouter(tags=["safeteen-incident-report"])


def _resolve_image_content_type(content_type: str | None, filename: str) -> str:
    """클라이언트가 content-type을 안 실어 보내거나(application/octet-stream) 이미지가
    아닌 값을 보내면 파일 확장자로 추정하고, 그마저 실패하면 jpeg로 가정한다."""
    if content_type and content_type.startswith("image/"):
        return content_type
    guessed, _ = mimetypes.guess_type(filename)
    if guessed and guessed.startswith("image/"):
        return guessed
    return "image/jpeg"


@incident_report_router.post(
    "/incident-report",
    summary="경찰 제출용 피해 경위서 및 증거 제출 서식 자동 작성",
    responses={400: {"description": "situation이 비어있음"}},
)
async def generate_incident_report(
    situation: str = Form(...),
    file: UploadFile | None = File(default=None),
    use_case: IncidentReportUseCase = Depends(get_incident_report_use_case),
) -> IncidentReportResponse:
    image_bytes: bytes | None = None
    image_content_type: str | None = None
    if file is not None:
        image_bytes = await file.read()
        image_content_type = _resolve_image_content_type(file.content_type, file.filename or "image.jpg")

    try:
        result = await use_case.generate(
            IncidentReportCommand(
                situation=situation, image_bytes=image_bytes, image_content_type=image_content_type
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return to_response(result)
