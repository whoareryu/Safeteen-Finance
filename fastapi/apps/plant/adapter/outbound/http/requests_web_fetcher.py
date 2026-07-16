from __future__ import annotations

import requests

from plant.app.ports.output.web_fetcher_port import WebFetcherPort

_USER_AGENT = "whoareryu-plant-crawler/1.0"


class RequestsWebFetcher(WebFetcherPort):
    def __init__(self, timeout: float = 10.0, user_agent: str = _USER_AGENT) -> None:
        self._timeout = timeout
        self._user_agent = user_agent

    def fetch(self, url: str) -> str:
        response = requests.get(url, timeout=self._timeout, headers={"User-Agent": self._user_agent})
        response.raise_for_status()
        return response.text
