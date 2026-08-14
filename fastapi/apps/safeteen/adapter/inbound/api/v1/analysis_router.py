from __future__ import annotations

import mimetypes

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from safeteen.adapter.inbound.api.schemas.analysis_schema import AnalysisResultResponse
from safeteen.adapter.inbound.mappers.analysis_mapper import to_response
from safeteen.app.dtos.analysis_dto import AnalyzeCommand
from safeteen.app.ports.input.analysis_use_case import AnalysisUseCase
from safeteen.dependencies.analysis_provider import get_analysis_use_case

analysis_router = APIRouter(tags=["safeteen-analysis"])


def _resolve_image_content_type(content_type: str | None, filename: str) -> str:
    """클라이언트가 content-type을 안 실어 보내거나(application/octet-stream) 이미지가
    아닌 값을 보내면 파일 확장자로 추정하고, 그마저 실패하면 jpeg로 가정한다."""
    if content_type and content_type.startswith("image/"):
        return content_type
    guessed, _ = mimetypes.guess_type(filename)
    if guessed and guessed.startswith("image/"):
        return guessed
    return "image/jpeg"


@analysis_router.post(
    "/analyze",
    summary="SNS 불법 금융 광고 텍스트/이미지 위험도 분석",
    responses={400: {"description": "text와 file이 모두 비어있음"}},
)
async def analyze(
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    use_case: AnalysisUseCase = Depends(get_analysis_use_case),
) -> AnalysisResultResponse:
    image_bytes: bytes | None = None
    image_content_type: str | None = None
    if file is not None:
        image_bytes = await file.read()
        image_content_type = _resolve_image_content_type(file.content_type, file.filename or "image.jpg")

    try:
        result = await use_case.analyze(
            AnalyzeCommand(text=text, image_bytes=image_bytes, image_content_type=image_content_type)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return to_response(result)
