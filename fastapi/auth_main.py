"""인증 게이트웨이 엔트리포인트 — auth.whoareryu.cloud (auth-gateway-harness.md 2.4).

기존 main.py(api.whoareryu.cloud)와 같은 코드베이스를 공유하지만 별도 프로세스로
띄운다. JWT_PRIVATE_KEY는 이 프로세스에만 있으면 된다 — main.py는
JWT_PUBLIC_KEY만으로 core.dependencies를 통해 토큰을 검증한다.
"""
import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent
_apps_root = _backend_root / "apps"
for _path in (_backend_root, _apps_root):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from dotenv import load_dotenv

load_dotenv(_backend_root / ".env")

from fastapi import FastAPI

from apps.auth.adapter.inbound.api.v1.mobile_auth_router import mobile_auth_router
from apps.auth.router import jwks_router, router as auth_router

app = FastAPI(
    title="whoareryu Auth",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(auth_router)
app.include_router(jwks_router)
app.include_router(mobile_auth_router)


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}
