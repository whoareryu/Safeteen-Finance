from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RestaurantBrowseRow:
    """목록·검색 풀용 — 필요 컬럼만 projection."""

    id: int
    name: str
    store_name: str
    branch_name: str
    category_slug: str
    category_label: str
    biz_mid_name: str
    biz_minor_name: str
    ksic_name: str
    biz_number: str
    district: str
    sigungu_name: str
    latitude: float | None
    longitude: float | None
    road_address: str = ""
    parcel_address: str = ""
    image_url: str = ""
