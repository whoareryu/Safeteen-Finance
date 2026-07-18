"""Pixabay 이미지 검색 — 식집사 튜토리얼용 무료 실사 사진 조회."""

from __future__ import annotations

import urllib.parse

from plant.adapter.outbound.http.http_util import http_get_bytes, http_get_json
from plant.config.external_settings import get_external_settings

# Pixabay는 per_page 최소값이 3이다.
_PER_PAGE = 3

# Pixabay CDN(get/*)은 기본 Python-urllib User-Agent를 봇으로 간주해 403을 반환한다.
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; whoareryu-plant-tutorial/1.0)"}


def search_first_photo(query: str) -> dict:
    settings = get_external_settings()
    if not settings.pixabay_configured:
        return {"error": "PIXABAY_API_KEY 가 fastapi/.env 에 없습니다."}

    params = {
        "key": settings.pixabay_api_key,
        "q": query,
        "image_type": "photo",
        "safesearch": "true",
        "per_page": str(_PER_PAGE),
    }
    url = "https://pixabay.com/api/?" + urllib.parse.urlencode(params)
    status, data = http_get_json(url, headers=_HEADERS)
    if status != 200:
        msg = data.get("message") if isinstance(data, dict) else "Pixabay 요청 실패"
        return {"error": str(msg)}

    hits = data.get("hits") or []
    if not hits:
        return {"error": "검색 결과가 없습니다."}

    first = hits[0]
    return {
        "source_id": str(first.get("id")),
        "image_url": first.get("webformatURL"),
    }


def download_photo(image_url: str) -> dict:
    status, body, content_type = http_get_bytes(image_url, headers=_HEADERS)
    if status != 200 or not body:
        return {"error": f"이미지 다운로드 실패 (status={status})"}
    return {"data": body, "content_type": content_type or "image/jpeg"}
