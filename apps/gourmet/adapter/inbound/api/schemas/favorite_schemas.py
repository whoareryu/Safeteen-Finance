from pydantic import BaseModel, Field


class FavoriteToggleRequest(BaseModel):
    store_id: int = Field(..., ge=1, description="카드·상세에 표시된 매장 id")


class FavoriteToggleResponse(BaseModel):
    store_id: int
    favorited: bool
    message: str


class FavoriteCardItem(BaseModel):
    store_id: int
    restaurant_id: int
    name: str
    image_url: str = ""
    district: str = ""
    category_slug: str | None = None
    category_label: str | None = None
    signature_menu: str = ""


class FavoriteCheckResponse(BaseModel):
    favorited_store_ids: list[int]
