"""날씨 — OpenWeatherMap (``backend/.env``)."""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from restaurant.adapter.outbound.http.openweather_client import fetch_current_weather

router = APIRouter(tags=["weather"])


@router.get("/weather")
def read_weather(
    lat: float | None = Query(None),
    lon: float | None = Query(None),
):
    return fetch_current_weather(lat=lat, lon=lon)


@router.get("/weather/icon")
def weather_icon(code: str = Query(..., min_length=2, max_length=8)):
    """OpenWeather 아이콘 PNG — CDN 리다이렉트."""
    safe = "".join(c for c in code if c.isalnum() or c in "-_")
    return RedirectResponse(
        url=f"https://openweathermap.org/img/wn/{safe}@2x.png",
        status_code=302,
    )
