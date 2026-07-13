from __future__ import annotations

import urllib.parse

from plant.app.ports.output.coupang_link_port import CoupangLinkPort


class CoupangSearchLinkAdapter(CoupangLinkPort):
    """Partners API 키 없이 쿠팡 검색 URL을 생성한다(v1)."""

    _SEARCH_URL = "https://www.coupang.com/np/search"

    def build_link(self, keyword: str) -> str:
        return f"{self._SEARCH_URL}?{urllib.parse.urlencode({'q': keyword})}"
