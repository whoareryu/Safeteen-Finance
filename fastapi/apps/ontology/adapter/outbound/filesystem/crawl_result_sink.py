from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from ontology.app.dtos.crawler_dto import CrawlResultDto
from ontology.app.ports.output.crawl_result_sink_port import CrawlResultSinkPort


class JsonlCrawlResultSink(CrawlResultSinkPort):
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, result: CrawlResultDto) -> str:
        domain = urlparse(result.source_url).netloc.replace(":", "_") or "unknown"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self._base_dir / f"{domain}_{timestamp}.jsonl"

        with path.open("w", encoding="utf-8") as f:
            for page in result.pages:
                line = {
                    "url": page.url,
                    "title": page.title,
                    "text": page.text,
                    "links": page.links,
                    "keyword": result.keyword,
                    "source_url": result.source_url,
                    "crawled_at": timestamp,
                }
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

        return str(path)
