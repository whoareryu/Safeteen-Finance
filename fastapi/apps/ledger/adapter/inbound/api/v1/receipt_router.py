from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from apps.auth.dependencies import get_current_user
from apps.auth.user_model import User

from ledger.adapter.inbound.api.schemas.receipt_schema import ReceiptResponse
from ledger.adapter.inbound.mappers.receipt_mapper import to_response
from ledger.app.dtos.receipt_dto import ReceiptUploadCommand
from ledger.app.ports.input.receipt_use_case import ReceiptUseCase
from ledger.dependencies.receipt_provider import get_receipt_use_case

receipt_router = APIRouter(prefix="/receipts", tags=["ledger-receipts"])


@receipt_router.post("/upload", summary="영수증 사진 업로드 → S3 저장 + Gemini Vision 추출")
async def upload_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    use_case: ReceiptUseCase = Depends(get_receipt_use_case),
) -> ReceiptResponse:
    content = await file.read()
    command = ReceiptUploadCommand(
        owner_user_id=current_user.id,
        filename=file.filename or "receipt.jpg",
        content_type=file.content_type or "image/jpeg",
        data=content,
    )
    result = await use_case.upload(command)
    return to_response(result)


@receipt_router.get("", summary="내 영수증 목록 조회")
async def list_receipts(
    current_user: User = Depends(get_current_user),
    use_case: ReceiptUseCase = Depends(get_receipt_use_case),
) -> list[ReceiptResponse]:
    results = await use_case.list_by_owner(current_user.id)
    return [to_response(result) for result in results]


@receipt_router.get("/{receipt_id}", summary="영수증 상세 조회")
async def get_receipt(
    receipt_id: int,
    use_case: ReceiptUseCase = Depends(get_receipt_use_case),
) -> ReceiptResponse:
    result = await use_case.get(receipt_id)
    return to_response(result)
