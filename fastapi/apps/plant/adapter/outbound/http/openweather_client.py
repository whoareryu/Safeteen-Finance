"""OpenWeatherMap — 현재 날씨(식물 케어 판단용: 온도/습도/일조 상태)."""

from __future__ import annotations

import urllib.parse

from plant.adapter.outbound.http.http_util import http_get_json
from plant.config.external_settings import get_external_settings


def fetch_current_weather(region: str | None = None) -> dict:
    settings = get_external_settings()
    if not settings.openweather_configured:
        return {"error": "OPENWEATHER_API_KEY 가 fastapi/.env 에 없습니다."}

    city = region or settings.openweather_city
    params = {
        "appid": settings.openweather_api_key,
        "units": "metric",
        "lang": "kr",
        "q": city,
    }
    url = "https://api.openweathermap.org/data/2.5/weather?" + urllib.parse.urlencode(params)
    status, data = http_get_json(url)
    if status != 200:
        msg = data.get("message") if isinstance(data, dict) else "OpenWeather 요청 실패"
        return {"error": str(msg)}

    main = data.get("main") or {}
    weather = (data.get("weather") or [{}])[0]
    temp = main.get("temp")
    humidity = main.get("humidity")
    description = weather.get("description")
    if temp is None or humidity is None or not description:
        return {"error": "날씨 데이터 형식이 올바르지 않습니다."}

    return {
        "region": data.get("name") or city,
        "temp_c": float(temp),
        "humidity_pct": float(humidity),
        "sunlight_desc": description,
    }
