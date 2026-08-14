import sys
from contextlib import asynccontextmanager
from pathlib import Path

_backend_root = Path(__file__).resolve().parent
_apps_root = _backend_root / "apps"
for _path in (_backend_root, _apps_root):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import logging

from urllib.parse import urlencode

from dotenv import load_dotenv
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv(_backend_root / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.db_health_adapter import DbHealthAdapter
from core.database import dispose_engine, get_db, init_db, init_engine
from core.llm.ollama_chat_orchestrator import OllamaChatOrchestrator
from core.infra.secret_manager import secret_manager

try:
    from doro.app.doro_director import DoroDirector
except ImportError:
    DoroDirector = None  # type: ignore[misc, assignment]

_faker = OllamaChatOrchestrator()


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
    # whoareryu.cloud는 Vercel 프로젝트 연결을 해제했다 — 새 프로덕션 도메인이 정해지면 여기에 추가한다.
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 브라우저 직접 접근 게이트: '/', '/docs', '/redoc', '/openapi.json'만 Google
#    로그인(OWNER_EMAIL)으로 막는다. /api/* 등 www 프론트엔드 호출은 대상 아님. ──
from apps.auth.browser_gate_router import GATED_PATHS, browser_gate_router  # noqa: E402
from apps.auth.owner_session import is_valid_owner_token  # noqa: E402


@app.middleware("http")
async def _google_browser_gate(request: Request, call_next):
    if request.url.path in GATED_PATHS and not is_valid_owner_token(
        request.cookies.get("wr_docs_gate")
    ):
        next_qs = urlencode({"next": request.url.path})
        return RedirectResponse(f"/auth/google/browser-login?{next_qs}")
    return await call_next(request)


from admin.adapter.inbound.api import admin_app_router
from ontology.adapter.inbound.api import ontology_router
from community.adapter.inbound.api import chef_router

from ontology.adapter.inbound.api.v1.sentiment_router import sentiment_router
from ontology.adapter.inbound.api.v1.video_router import video_router
from ontology.adapter.inbound.api.v1.anomaly_router import anomaly_router
from ledger.adapter.inbound.api import ledger_router
from safeteen.adapter.inbound.api import safeteen_router
from apps.auth.admin_router import admin_router
# 로그인(Google/Naver/Kakao)·회원가입 동의는 auth_main.py(auth.whoareryu.cloud)로
# 이동했다 — 이 백엔드는 RS256 공개키로 토큰을 검증만 한다(core.dependencies).

# ── Composition root: ChefTaskDispatcher → Maestro 주입 ──────────────────
from apps.auth.owner_session import is_valid_owner_token
from community.adapter.outbound.chef_task_dispatcher import ChefTaskDispatcher
from community.dependencies.email_provider import get_email_use_case
from ontology.app.ports.output.owner_gate_port import OwnerGatePort
from ontology.app.use_cases.maestro_router_interactor import MaestroInteractor
from ontology.dependencies.maestro_router_provider import (
    register_dispatch_factory,
    get_sommelier_use_case,
    get_lens_use_case,
)


class _OwnerGateAdapter(OwnerGatePort):
    def is_owner(self, owner_session: str | None) -> bool:
        return is_valid_owner_token(owner_session)


register_dispatch_factory(
    lambda: MaestroInteractor(
        sommelier=get_sommelier_use_case(),
        lens=get_lens_use_case(),
        llm=OllamaChatOrchestrator(),
        dispatcher=ChefTaskDispatcher(
            email=get_email_use_case(),
        ),
        owner_gate=_OwnerGateAdapter(),
    )
)

from fastapi.staticfiles import StaticFiles

from ontology.adapter.outbound.s3.s3_image_storage_gateway import S3ImageStorageGateway

# ── Composition root: ledger 전용 영수증 이미지 저장소(S3) + Gemini Vision 파서 주입 ──
from ledger.adapter.outbound.llm.gemini_receipt_vision_parser_adapter import (
    GeminiReceiptVisionParserAdapter,
)
from ledger.dependencies.receipt_provider import (
    register_image_storage_factory as register_ledger_image_storage_factory,
    register_vision_parser_factory as register_ledger_vision_parser_factory,
)

register_ledger_image_storage_factory(
    lambda: S3ImageStorageGateway(
        bucket=secret_manager.get_secret("LEDGER_S3_BUCKET", ""),
        region=secret_manager.get_secret("AWS_REGION", "ap-northeast-2"),
        prefix="receipts",
    )
)
register_ledger_vision_parser_factory(lambda: GeminiReceiptVisionParserAdapter())
# ─────────────────────────────────────────────────────────────────────────

# ── Composition root: 이미지 생성(SDXL Turbo) 결과물 정적 서빙 ────────────────
_ontology_generated_media_dir = _backend_root / "apps/ontology/resources/generated_images"
_ontology_generated_media_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/media/generated",
    StaticFiles(directory=str(_ontology_generated_media_dir), check_dir=False),
    name="ontology-generated-media",
)
# ─────────────────────────────────────────────────────────────────────────

app.include_router(ontology_router, prefix="/api")
app.include_router(admin_app_router, prefix="/api")
app.include_router(chef_router, prefix="/api")
app.include_router(sentiment_router, prefix="/api")
app.include_router(video_router, prefix="/api")
app.include_router(anomaly_router, prefix="/api")
app.include_router(ledger_router, prefix="/api")
app.include_router(safeteen_router, prefix="/api")
app.include_router(browser_gate_router)
app.include_router(admin_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FAST API 메인 페이지", "docs": "/docs"}


@app.get("/auth/owner-check")
def owner_check(wr_owner_session: str | None = Cookie(default=None)) -> dict:
    """owner_session.py는 RS256 로그인 재작성과 무관해 이 백엔드에 그대로 남긴다.

    www의 lib/auth.ts `checkOwner()`가 이 경로를 호출해 community(이메일 발송·
    주소록) 등 owner 전용 기능 접근 가능 여부를 판단한다.
    """
    return {"is_owner": is_valid_owner_token(wr_owner_session)}


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
    return await DbHealthAdapter.db_time_check(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
