"""Windows·uvicorn 공통 진입점 — `python run_server.py` (backend 루트).

`python -m uvicorn apps.main:app` 대신 사용하면 psycopg async + ProactorEventLoop 오류를 피합니다.
"""

from __future__ import annotations

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "apps.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        loop="asyncio",
    )
