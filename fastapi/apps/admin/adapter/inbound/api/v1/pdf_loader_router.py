from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from admin.adapter.inbound.mappers.pdf_loader_mapper import to_response
from admin.adapter.inbound.api.schemas.pdf_loader_schema import PdfSummaryResponse
from admin.app.dtos.pdf_loader_dto import PdfUploadCommand
from admin.app.ports.input.pdf_loader_use_case import PdfLoaderUseCase
from admin.dependencies.pdf_loader_provider import get_pdf_loader_use_case

pdf_loader_router = APIRouter(prefix="/pdf", tags=["pdf-loader"])


@pdf_loader_router.post("/summarize", summary="PDF 업로드 → 텍스트 추출 → 요약")
async def summarize_pdf(
    file: UploadFile = File(...),
    use_case: PdfLoaderUseCase = Depends(get_pdf_loader_use_case),
) -> PdfSummaryResponse:
    content = await file.read()
    command = PdfUploadCommand(
        filename=file.filename or "unknown.pdf",
        content_type=file.content_type or "application/pdf",
        data=content,
    )
    result = await use_case.summarize(command)
    return to_response(result)


@pdf_loader_router.get("/{document_id}", summary="추출·요약 결과 조회")
async def get_pdf_summary(
    document_id: int,
    use_case: PdfLoaderUseCase = Depends(get_pdf_loader_use_case),
) -> PdfSummaryResponse:
    result = await use_case.get(document_id)
    return to_response(result)
