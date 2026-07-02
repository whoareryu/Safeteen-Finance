import sys
from contextlib import asynccontextmanager
from pathlib import Path

_backend_root = Path(__file__).resolve().parent
_apps_root = _backend_root / "apps"
for _path in (_backend_root, _apps_root):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import logging

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv(_backend_root / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.db_health_adapter import DbHealthAdapter
from core.database import dispose_engine, get_db, init_db, init_engine
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

try:
    from doro.app.doro_director import DoroDirector
except ImportError:
    DoroDirector = None  # type: ignore[misc, assignment]

try:
    from titanic.app.james_controller import JamesController
except ImportError:
    JamesController = None  # type: ignore[misc, assignment]

_faker = T1MidFakerOrchestrator()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="사용자 메시지")


class ChatResponse(BaseModel):
    reply: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_engine()
        await init_db()
    except Exception:
        logger.exception("데이터베이스 시작 초기화 실패")
    yield
    await dispose_engine()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://whoareryu.cloud",
        "https://www.whoareryu.cloud",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from titanic.adapter.inbound.api import titanic_router  # noqa: E402
from silicon_valley.adapter.inbound.api import silicon_valley_router
from ontology.adapter.inbound.api import ontology_router
from chef.adapter.inbound.api import chef_router

from restaurant.adapter.inbound.api import restaurant_router
from user.adapter.inbound.api import user_router
from apps.auth.auth_endpoints import auth_router, signup_router, login_router

# ── Composition root: ChefTaskDispatcher → Maestro 주입 ──────────────────
import os

from chef.adapter.outbound.chef_task_dispatcher import ChefTaskDispatcher
from chef.dependencies.email_provider import get_email_use_case
from chef.dependencies.spam_provider import get_spam_use_case
from ontology.app.use_cases.maestro_router_interactor import MaestroInteractor
from ontology.dependencies.maestro_router_provider import (
    register_dispatch_factory,
    get_sommelier_use_case,
    get_lens_use_case,
)

register_dispatch_factory(
    lambda: MaestroInteractor(
        sommelier=get_sommelier_use_case(),
        lens=get_lens_use_case(),
        llm=T1MidFakerOrchestrator(),
        dispatcher=ChefTaskDispatcher(
            email=get_email_use_case(),
            spam=get_spam_use_case(),
        ),
    )
)
# ─────────────────────────────────────────────────────────────────────────

app.include_router(ontology_router, prefix="/api")
app.include_router(titanic_router, prefix="/api")
app.include_router(silicon_valley_router, prefix="/api")
app.include_router(chef_router, prefix="/api")
app.include_router(restaurant_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(signup_router)
app.include_router(login_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FAST API 메인 페이지", "docs": "/docs"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """JSON 본문 `{"message": "..."}` 를 받아 ExaOne 답변 문자열을 반환합니다."""
    try:
        reply = await _faker.chat([{"role": "user", "content": req.message}])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ExaOne 호출 실패: {e!s}") from e
    return ChatResponse(reply=reply)


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
