from __future__ import annotations

import asyncio

from plant.adapter.outbound.http.openweather_client import fetch_current_weather
from plant.app.ports.output.weather_api_gateway import CurrentWeatherData, WeatherApiGateway


class OpenWeatherGateway(WeatherApiGateway):

    async def fetch_current(self, region: str) -> CurrentWeatherData:
        data = await asyncio.to_thread(fetch_current_weather, region)
        if "error" in data:
            raise ValueError(data["error"])
        return CurrentWeatherData(
            region=data["region"],
            temp_c=data["temp_c"],
            humidity_pct=data["humidity_pct"],
            sunlight_desc=data["sunlight_desc"],
        )
