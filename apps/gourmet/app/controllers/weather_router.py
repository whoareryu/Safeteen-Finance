"""날씨 — OpenWeatherMap (``backend/.env``)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from apps.gourmet.app.adapters.openweather_client import fetch_current_weather

router = APIRouter(tags=["weather"])


@router.get("/weather")
def read_weather(
    lat: float | None = Query(None),
    lon: float | None = Query(None),
):
    result = fetch_current_weather(lat=lat, lon=lon)
    if result.get("error"):
        err = str(result["error"])
        if "좌표" in err:
            raise HTTPException(status_code=400, detail=err)
        if "OPENWEATHER" in err or "없습니다" in err:
            raise HTTPException(status_code=503, detail=err)
        raise HTTPException(status_code=502, detail=err)
    return result


@router.get("/weather/icon")
def weather_icon(code: str = Query(..., min_length=2, max_length=8)):
    """OpenWeather 아이콘 PNG — CDN 리다이렉트."""
    safe = "".join(c for c in code if c.isalnum() or c in "-_")
    if not safe:
        raise HTTPException(status_code=400, detail="icon code 가 올바르지 않습니다.")
    return RedirectResponse(
        url=f"https://openweathermap.org/img/wn/{safe}@2x.png",
        status_code=302,
    )
