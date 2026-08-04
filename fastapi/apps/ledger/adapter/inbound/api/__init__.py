from fastapi import APIRouter

from ledger.adapter.inbound.api.v1.receipt_router import receipt_router

ledger_router = APIRouter(prefix="/ledger", tags=["ledger"])
ledger_router.include_router(receipt_router)

__all__ = ["ledger_router", "receipt_router"]
