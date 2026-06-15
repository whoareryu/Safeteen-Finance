"""Kakao Local API — 키워드 검색으로 전화·URL·좌표 보정."""

from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass

from restaurant.adapter.outbound.http.http_util import http_get_json
from restaurant.config.external_settings import get_external_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KakaoLookupResult:
    data: dict | None
    error_code: str | None = None
    error_message: str | None = None


def lookup_place(
    *,
    name: str,
    district: str = "",
    road_address: str = "",
) -> KakaoLookupResult:
    settings = get_external_settings()
    if not settings.kakao_configured:
        return KakaoLookupResult(None)

    query = " ".join(p for p in (name.strip(), district.strip()) if p)[:100]
    if not query:
        return KakaoLookupResult(None)

    params = urllib.parse.urlencode({"query": query, "size": "3"})
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?{params}"
    status, data = http_get_json(
        url,
        headers={"Authorization": f"KakaoAK {settings.kakao_rest_api_key}"},
    )
    if status != 200:
        logger.warning("[kakao] keyword search failed status=%s body=%s", status, data)
        code, msg = _parse_kakao_error(status, data)
        return KakaoLookupResult(None, error_code=code, error_message=msg)

    docs = data.get("documents") if isinstance(data, dict) else None
    if not docs:
        return KakaoLookupResult(None, error_code="no_match")

    pick = _best_document(docs, name=name, road_address=road_address)
    if pick is None:
        return KakaoLookupResult(None, error_code="no_match")

    phone = (pick.get("phone") or "").strip() or None
    place_url = (pick.get("place_url") or "").strip() or None
    category_name = (pick.get("category_name") or "").strip()
    x, y = pick.get("x"), pick.get("y")
    latitude = float(y) if y else None
    longitude = float(x) if x else None

    return KakaoLookupResult(
        {
            "phone": phone,
            "place_url": place_url,
            "kakao_category": category_name,
            "latitude": latitude,
            "longitude": longitude,
            "kakao_place_name": (pick.get("place_name") or "").strip(),
        }
    )


def _parse_kakao_error(status: int, data: object) -> tuple[str, str]:
    if status == 401:
        msg = ""
        if isinstance(data, dict):
            msg = str(data.get("message") or data.get("msg") or "")
        if "KA Header" in msg or "AccessDenied" in str(data):
            return (
                "wrong_key_type",
                "JavaScript 키가 아닌 REST API 키를 KAKAO_REST_API_KEY에 넣어 주세요.",
            )
        return ("unauthorized", "Kakao REST API 키가 올바르지 않습니다.")
    if status == 403:
        return ("forbidden", "Kakao 앱에서 로컬 API 사용 설정·플랫폼을 확인하세요.")
    return ("http_error", f"Kakao API 오류 (HTTP {status})")


def _best_document(
    docs: list[dict],
    *,
    name: str,
    road_address: str,
) -> dict | None:
    name_l = name.lower()
    addr_l = road_address.lower()
    best: dict | None = None
    best_score = -1
    for d in docs:
        pn = (d.get("place_name") or "").lower()
        addr = (d.get("road_address_name") or d.get("address_name") or "").lower()
        score = 0
        if name_l and name_l in pn:
            score += 3
        if addr_l and addr_l in addr:
            score += 2
        if d.get("phone"):
            score += 1
        if score > best_score:
            best_score = score
            best = d
    return best or (docs[0] if docs else None)

