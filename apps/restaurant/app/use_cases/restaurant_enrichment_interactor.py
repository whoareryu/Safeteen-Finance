"""외부 API 보강 — Kakao·LOCALDATA 실시간 조회 + DB 병합."""

from __future__ import annotations

import logging
import os

from sqlalchemy.orm import Session

from restaurant.adapter.outbound.http.kakao_local_client import lookup_place as kakao_lookup
from restaurant.adapter.outbound.http.localdata_client import lookup_store as localdata_lookup
from restaurant.config.external_settings import get_external_settings
from restaurant.adapter.outbound.pg.restaurant_pg_repository import RestaurantRepository
from restaurant.app.ports.input.restaurant_enrichment_use_case import RestaurantEnrichmentUseCase
from restaurant.adapter.inbound.api.schemas.restaurant_enrichment_schema import RestaurantEnrichmentSchema
from restaurant.app.dtos.restaurant_enrichment_dto import RestaurantEnrichmentQuery, RestaurantEnrichmentResponse
from restaurant.app.ports.output.restaurant_enrichment_repository import RestaurantEnrichmentRepository


logger = logging.getLogger(__name__)


def _source_note(
    configured: bool,
    env_key: str,
    *,
    used: bool,
    hint: str = "",
) -> dict:
    if not configured:
        return {
            "configured": False,
            "note": f"{env_key} 미설정 — backend/.env.example 참고",
        }
    note = "조회에 사용됨" if used else "키 설정됨 — 매칭 결과 없음"
    if hint:
        note = f"{note}. {hint}"
    return {"configured": True, "note": note}


def get_restaurant_enrichment(db: Session, restaurant_id: int) -> dict | None:
    settings = get_external_settings()
    row = RestaurantRepository().get_by_id(db, restaurant_id)
    if row is None:
        return None

    detail = row.to_detail_dict()
    phone = detail.get("phone")
    opening_hours = detail.get("opening_hours")
    closed_label = detail.get("closed_weekdays_label")
    instagram_url = detail.get("instagram_url")
    extra_images: list[str] = []
    kakao_used = False
    localdata_used = False
    kakao_hint = ""
    localdata_hint = ""

    name = row.display_name()
    district = row.district or row.sigungu_name or ""
    road = row.road_address or ""

    if settings.kakao_configured:
        try:
            result = kakao_lookup(name=name, district=district, road_address=road)
            if result.data:
                kakao_used = True
                if result.data.get("phone"):
                    phone = result.data["phone"]
                if result.data.get("place_url") and not instagram_url:
                    instagram_url = result.data["place_url"]
            elif result.error_message:
                kakao_hint = result.error_message
        except Exception:
            logger.exception("[enrichment] kakao lookup failed id=%s", restaurant_id)
            kakao_hint = "Kakao 조회 중 예외 발생"

    if settings.localdata_configured:
        try:
            ld, ld_err = localdata_lookup(name=name, district=district)
            if ld:
                localdata_used = True
                if ld.get("phone"):
                    phone = ld["phone"]
                if ld.get("opening_hours"):
                    opening_hours = ld["opening_hours"]
                if ld.get("closed_weekdays_label"):
                    closed_label = ld["closed_weekdays_label"]
            elif ld_err:
                localdata_hint = ld_err
        except Exception:
            logger.exception("[enrichment] localdata lookup failed id=%s", restaurant_id)
            localdata_hint = "LOCALDATA 조회 중 예외 발생"

    if row.image_url:
        extra_images = [row.image_url]

    sources = {
        "gemini": _source_note(
            bool((os.getenv("GEMINI_API_KEY") or "").strip()),
            "GEMINI_API_KEY",
            used=False,
        ),
        "kakao_local": _source_note(
            settings.kakao_configured,
            "KAKAO_REST_API_KEY",
            used=kakao_used,
            hint=kakao_hint,
        ),
        "localdata": _source_note(
            settings.localdata_configured,
            "LOCALDATA_API_KEY",
            used=localdata_used,
            hint=localdata_hint,
        ),
        "openweather": _source_note(
            settings.openweather_configured,
            "OPENWEATHER_API_KEY",
            used=False,
        ),
    }

    if kakao_used or localdata_used:
        msg = "외부 API 데이터를 반영했습니다."
    elif kakao_hint or localdata_hint:
        msg = " ".join(p for p in (kakao_hint, localdata_hint) if p)
    elif settings.kakao_configured or settings.localdata_configured:
        msg = "키는 설정됐으나 이 매장과 일치하는 외부 데이터가 없습니다."
    else:
        msg = "backend/.env 에 API 키를 설정하면 보강됩니다."

    return {
        "restaurant_id": restaurant_id,
        "phone": phone,
        "opening_hours": opening_hours,
        "closed_weekdays_label": closed_label,
        "instagram_url": instagram_url,
        "extra_images": extra_images,
        "sources": sources,
        "message": msg,
    }


class RestaurantEnrichmentInteractor(RestaurantEnrichmentUseCase):
    def __init__(self, repository: RestaurantEnrichmentRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: RestaurantEnrichmentSchema) -> RestaurantEnrichmentResponse:
        return await self.repository.introduce_myself(
            RestaurantEnrichmentQuery(id=schema.id, name=schema.name)
        )
