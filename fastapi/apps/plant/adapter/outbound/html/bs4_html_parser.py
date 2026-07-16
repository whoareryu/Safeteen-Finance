from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from plant.app.ports.output.html_parser_port import HtmlParserPort
from plant.domain.entities.raw_content_entity import RawContentEntity


class Bs4HtmlParser(HtmlParserPort):
    def extract_links(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        return [urljoin(base_url, a["href"]).split("#")[0] for a in soup.find_all("a", href=True)]

    def extract_content(self, html: str, url: str, keyword: str) -> RawContentEntity | None:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator=" ", strip=True)
        if keyword.lower() not in text.lower():
            return None

        title = soup.title.get_text(strip=True) if soup.title else ""
        return RawContentEntity(
            url=url,
            keyword=keyword,
            title=title,
            text=text,
            extracted_at=datetime.now(timezone.utc).isoformat(),
        )
