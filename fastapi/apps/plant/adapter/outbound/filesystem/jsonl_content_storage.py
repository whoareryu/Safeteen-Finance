from __future__ import annotations

import json
import re
from pathlib import Path

from plant.app.ports.output.content_storage_port import ContentStoragePort
from plant.domain.entities.raw_content_entity import RawContentEntity

_SLUG_PATTERN = re.compile(r"[^0-9A-Za-z가-힣]+")


def _slugify(keyword: str) -> str:
    slug = _SLUG_PATTERN.sub("_", keyword).strip("_")
    return slug or "dataset"


class JsonlContentStorage(ContentStoragePort):
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: RawContentEntity) -> str:
        path = self._base_dir / f"{_slugify(content.keyword)}.jsonl"
        line = {
            "url": content.url,
            "keyword": content.keyword,
            "title": content.title,
            "text": content.text,
            "extracted_at": content.extracted_at,
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
        return str(path)
