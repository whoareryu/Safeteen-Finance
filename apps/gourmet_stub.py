from __future__ import annotations

from fastapi import APIRouter, Header


def create_gourmet_stub_router() -> APIRouter:
    """
    Gourmet 모듈이 없는 환경에서 프론트(마이페이지/즐겨찾기)가 404로 깨지지 않도록
    최소 응답만 제공하는 스텁 라우터.
    """

    router = APIRouter(prefix="/gourmet", tags=["gourmet-stub"])

    @router.get("/favorites/store-ids")
    async def favorite_store_ids(x_user_id: str | None = Header(default=None)) -> dict[str, list[int]]:
        # 프론트는 { favorited_store_ids: number[] } 를 기대함
        _ = x_user_id
        return {"favorited_store_ids": []}

    @router.get("/favorites")
    async def favorites_list(x_user_id: str | None = Header(default=None)) -> list[dict]:
        _ = x_user_id
        return []

    @router.post("/favorites/toggle")
    async def favorites_toggle() -> dict[str, object]:
        return {
            "favorited": False,
            "message": "gourmet 모듈이 없어 즐겨찾기를 저장할 수 없습니다.",
        }

    return router

