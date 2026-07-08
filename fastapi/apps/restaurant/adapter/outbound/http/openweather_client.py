"""OpenWeatherMap — 현재 날씨."""

from __future__ import annotations

import urllib.parse

from restaurant.adapter.outbound.http.http_util import http_get_json
from restaurant.config.external_settings import get_external_settings


def fetch_current_weather(
    *,
    lat: float | None = None,
    lon: float | None = None,
) -> dict:
    settings = get_external_settings()
    if not settings.openweather_configured:
        return {"error": "OPENWEATHER_API_KEY 가 backend/.env 에 없습니다."}

    params: dict[str, str] = {
        "appid": settings.openweather_api_key,
        "units": "metric",
        "lang": "kr",
    }
    location_label: str
    if lat is not None and lon is not None:
        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
            return {"error": "위치 좌표가 올바르지 않습니다."}
        params["lat"] = str(lat)
        params["lon"] = str(lon)
        location_label = "현재 위치"
        location_source = "geolocation"
    else:
        params["q"] = settings.openweather_city
        location_label = settings.openweather_city
        location_source = "city"

    url = (
        "https://api.openweathermap.org/data/2.5/weather?"
        + urllib.parse.urlencode(params)
    )
    status, data = http_get_json(url)
    if status != 200:
        msg = data.get("message") if isinstance(data, dict) else "OpenWeather 요청 실패"
        return {"error": str(msg)}

    main = data.get("main") or {}
    weather = (data.get("weather") or [{}])[0]
    temp = main.get("temp")
    description = weather.get("description")
    icon = weather.get("icon")
    if temp is None or not description or not icon:
        return {"error": "날씨 데이터 형식이 올바르지 않습니다."}

    return {
        "city": data.get("name") or location_label,
        "temp": round(float(temp)),
        "description": description,
        "icon": icon,
        "iconUrl": f"/api/weather/icon?code={urllib.parse.quote(str(icon))}",
        "locationSource": location_source,
    }

