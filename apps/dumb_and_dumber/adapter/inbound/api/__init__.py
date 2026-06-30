from fastapi import APIRouter

dumb_and_dumber_router = APIRouter(prefix="/dumb-and-dumber", tags=["dumb-and-dumber"])

__all__ = ["dumb_and_dumber_router"]
