"""태그 slug 정규화."""

from __future__ import annotations

import re


def tag_slug_from_label(label: str) -> str:
    text = (label or "").strip().lower()
    if not text:
        return "tag"
    slug = re.sub(r"[^\w가-힣]+", "-", text, flags=re.UNICODE)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return (slug[:64] or "tag")
