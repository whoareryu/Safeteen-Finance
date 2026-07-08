"""위치·거리 — 순수 도메인 계산 (인프라 비의존).

헥사고날: 도메인 레이어. ORM/interactor 등 상위 레이어가 이 함수를 사용한다.
"""

from __future__ import annotations

import math

from restaurant.data.district_coordinates import DISTRICT_COORDINATES, SEOUL_CENTER

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """두 좌표 사이 거리(km)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def coords_for_district(district: str, restaurant_id: int) -> tuple[float, float]:
    """상권 중심 + 매장별 소폭 오프셋(약 500m 이내)."""
    base = DISTRICT_COORDINATES.get(district, SEOUL_CENTER)
    jitter_lat = ((restaurant_id * 17) % 100 - 50) / 5000.0
    jitter_lng = ((restaurant_id * 31) % 100 - 50) / 5000.0
    return base[0] + jitter_lat, base[1] + jitter_lng


def entity_lat_lng(entity: object) -> tuple[float, float]:
    """좌표가 없으면 district+id 로 대략 좌표."""
    lat = getattr(entity, "latitude", None)
    lng = getattr(entity, "longitude", None)
    if lat is not None and lng is not None:
        return float(lat), float(lng)
    district = str(getattr(entity, "district", "") or "")
    rid = int(getattr(entity, "id", 0) or 0)
    return coords_for_district(district, rid)


def distance_km_to_entity(entity: object, user_lat: float, user_lng: float) -> float:
    rlat, rlng = entity_lat_lng(entity)
    return haversine_km(user_lat, user_lng, rlat, rlng)


def parse_user_location(
    lat: float | None, lng: float | None
) -> tuple[float, float] | None:
    if lat is None or lng is None:
        return None
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lng <= 180.0):
        return None
    return lat, lng
