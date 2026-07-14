"""외부 REST 호출 — stdlib only."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def http_get_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 12.0,
) -> tuple[int, Any]:
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return e.code, {"message": raw[:500]}
    except urllib.error.URLError as e:
        return 0, {"message": str(e.reason)}


def http_get_text(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 12.0,
) -> tuple[int, str]:
    """XML 등 비-JSON 응답용 — 원문 텍스트를 그대로 반환한다."""
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        return 0, str(e.reason)
