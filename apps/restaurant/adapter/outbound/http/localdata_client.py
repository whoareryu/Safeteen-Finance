"""LOCALDATA — 공공데이터포털 Open API (구 localdata.go.kr REST는 종료)."""

from __future__ import annotations

import logging
import urllib.parse

from restaurant.adapter.outbound.http.http_util import http_get_json
from restaurant.config.external_settings import get_external_settings

logger = logging.getLogger(__name__)


def lookup_store(*, name: str, district: str = "") -> tuple[dict | None, str | None]:
    """(결과 dict, 오류 안내 문구)."""
    settings = get_external_settings()
    if not settings.localdata_configured:
        return None, None

    store_name = name.strip()[:80]
    if not store_name:
        return None, None

    if settings.localdata_api_url:
        return _lookup_via_data_go_kr(settings, store_name, district)

    return _lookup_via_legacy_localdata(settings, store_name, district)


def _lookup_via_data_go_kr(
    settings, store_name: str, district: str
) -> tuple[dict | None, str | None]:
    base = settings.localdata_api_url
    params: dict[str, str] = {
        "serviceKey": settings.localdata_api_key,
        "pageNo": "1",
        "numOfRows": "5",
        "type": "json",
        "resultType": "json",
        "bizesNm": store_name,
    }
    if district.strip():
        params["rdnWhlAddr"] = district.strip()[:60]

    sep = "&" if "?" in base else "?"
    url = base + sep + urllib.parse.urlencode(params)
    status, data = http_get_json(url, timeout=20.0)
    if status != 200:
        logger.warning("[localdata] data.go.kr failed status=%s", status)
        return None, "공공데이터포털 API 호출 실패 — LOCALDATA_API_URL·인증키를 확인하세요."

    parsed = _parse_enrichment_fields(data)
    if parsed:
        return parsed, None
    return None, "응답은 받았으나 매칭된 업소가 없습니다."


def _lookup_via_legacy_localdata(
    settings, store_name: str, district: str
) -> tuple[dict | None, str | None]:
    params = {
        "authKey": settings.localdata_api_key,
        "resultType": "json",
        "localdataYn": "Y",
        "bizesNm": store_name,
        "pageSize": "5",
        "pageIndex": "1",
    }
    if district.strip():
        params["rdnWhlAddr"] = district.strip()[:60]

    url = settings.localdata_base_url + "?" + urllib.parse.urlencode(params)
    status, data = http_get_json(url, timeout=15.0)
    if status != 200:
        return None, "LOCALDATA 구 API 호출 실패"

    header = (data.get("result") or {}).get("header") if isinstance(data, dict) else {}
    process = (header or {}).get("process") or {}
    code = str(process.get("code", ""))
    if code == "999":
        return (
            None,
            "localdata.go.kr 직접 API는 종료됐습니다. "
            "공공데이터포털 활용신청 URL을 LOCALDATA_API_URL 에 넣어 주세요.",
        )

    parsed = _parse_enrichment_fields(data)
    return parsed, None if parsed else "매칭된 업소가 없습니다."


def _parse_enrichment_fields(data: object) -> dict | None:
    rows = _extract_rows(data)
    if not rows:
        return None
    row = rows[0]
    phone = _first_str(row, "siteTel", "sitePhone", "telNo", "phone", "siteTelNo")
    hours = _first_str(row, "bizHour", "openTime", "operTime", "openHours")
    closed = _first_str(row, "holiday", "restDay", "dayOff", "restDt")
    status_nm = _first_str(row, "bizStatNm", "statusNm", "trdStateNm", "stateNm")

    out: dict = {}
    if phone:
        out["phone"] = phone
    if hours:
        out["opening_hours"] = hours
    if closed:
        out["closed_weekdays_label"] = closed
    elif status_nm:
        out["closed_weekdays_label"] = status_nm
    return out or None


def _extract_rows(data: object) -> list[dict]:
    if not isinstance(data, dict):
        return []

    for path in (
        lambda d: (d.get("response") or {}).get("body", {}).get("items"),
        lambda d: (d.get("body") or {}).get("items"),
        lambda d: d.get("items"),
        lambda d: (d.get("result") or {}).get("body", {}).get("items"),
    ):
        try:
            items = path(data)
        except (TypeError, AttributeError):
            continue
        if isinstance(items, list):
            return [x for x in items if isinstance(x, dict)]
        if isinstance(items, dict):
            row = items.get("item") or items.get("row")
            if isinstance(row, list):
                return [x for x in row if isinstance(x, dict)]
            if isinstance(row, dict):
                return [row]
    return []


def _first_str(row: dict, *keys: str) -> str | None:
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return None

