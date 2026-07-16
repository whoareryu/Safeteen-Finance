from __future__ import annotations

import httpx

from ontology.app.ports.output.web_fetcher_port import WebFetcherPort

_USER_AGENT = "whoareryu-ontology-bot/1.0"


class HttpxWebFetcherGateway(WebFetcherPort):
    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": _USER_AGENT})
            response.raise_for_status()
            return response.text
