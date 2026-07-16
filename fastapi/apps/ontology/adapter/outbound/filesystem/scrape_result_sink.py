from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from ontology.app.dtos.scraper_dto import ScrapeResultDto
from ontology.app.ports.output.scrape_result_sink_port import ScrapeResultSinkPort


class JsonlScrapeResultSink(ScrapeResultSinkPort):
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, result: ScrapeResultDto) -> str:
        domain = urlparse(result.source_url).netloc.replace(":", "_") or "unknown"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self._base_dir / f"{domain}_{timestamp}.jsonl"

        with path.open("w", encoding="utf-8") as f:
            for match in result.matches:
                line = {
                    "url": result.source_url,
                    "keyword": result.keyword,
                    "match": match,
                    "scraped_at": timestamp,
                }
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

        return str(path)
