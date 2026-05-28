import asyncio
import sys
from pathlib import Path

# Windows: psycopg async는 ProactorEventLoop와 호환되지 않음
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# `cd backend/apps` 후 `uvicorn main:app` 실행 시, cwd만 path에 들어가 `apps` 패키지를 못 찾음 → backend 루트 추가
_backend_root = Path(__file__).resolve().parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from apps.auth.auth_router import (
        LoginRequest,
        SignupRequest,
        UserPublic,
        router as auth_router,
    )
    from apps.auth.auth_router import _db_unavailable as auth_db_unavailable
    from apps.auth.auth_router import login as auth_login
    from apps.auth.auth_router import signup as auth_signup
    from apps.auth.user_model import User  # noqa: F401 — Base.metadata 등록

    _AUTH_AVAILABLE = True
except ModuleNotFoundError:
    # 현재 저장소에서 auth 모듈이 삭제/이동된 상태일 수 있음.
    # Titaninc 업로드/조회 등 다른 기능은 실행되도록 서버 기동은 보장한다.
    _AUTH_AVAILABLE = False

    logging.getLogger(__name__).warning("apps.auth 모듈을 찾지 못해 인증 라우트를 비활성화합니다.")

    auth_router = APIRouter()

    class LoginRequest(BaseModel):
        username: str | None = None
        password: str | None = None

    class SignupRequest(BaseModel):
        username: str | None = None
        email: str | None = None
        nickname: str | None = None
        password: str | None = None

    class UserPublic(BaseModel):
        ok: bool = False
        message: str = "auth 모듈이 비활성화되어 있습니다."

    def auth_db_unavailable() -> None:
        raise HTTPException(status_code=503, detail="인증 기능이 비활성화되어 있습니다.")

    def auth_login(body: LoginRequest, db: AsyncSession) -> None:  # type: ignore[override]
        auth_db_unavailable()

    def auth_signup(body: SignupRequest, db: AsyncSession) -> None:  # type: ignore[override]
        auth_db_unavailable()
try:
    from apps.secom.app.controllers.user_controller import router as secom_router
except ModuleNotFoundError:
    secom_router = APIRouter()

try:
    from apps.gourmet.app.controllers import router as gourmet_router
except ModuleNotFoundError:
    gourmet_router = APIRouter()

try:
    from apps.gourmet.app.controllers.weather_router import router as weather_router
except ModuleNotFoundError:
    weather_router = APIRouter()

try:
    from apps.matrix.app.keymaker import MissingGeminiKeyError, keymaker
except ModuleNotFoundError:
    class MissingGeminiKeyError(Exception):  # type: ignore[no-redef]
        pass

    keymaker = None  # type: ignore[assignment]

try:
    from apps.adapters.db_health_adapter import SqlAlchemyDbHealthAdapter
except ModuleNotFoundError:
    class SqlAlchemyDbHealthAdapter:  # type: ignore[no-redef]
        def __init__(self, *_: object, **__: object) -> None:
            pass

        async def check_sql_time(self) -> dict:
            return {"error": True, "message": "DB health adapter 비활성화"}

from urllib.parse import urlparse

from apps.database import (
    DATABASE_INIT_ERROR,
    DATABASE_URL,
    get_db,
    get_sync_db,
    init_db,
)

try:
    from apps.doro.app.doro_director import DoroDirector
except ModuleNotFoundError:
    DoroDirector = None  # type: ignore[assignment]

from apps.titanic.adapter.inbound.api.v1 import router as titanic_router
from apps.titanic.app.use_cases.titanic_schemas import ChatMessage, ChatRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        host = urlparse(DATABASE_URL or "").hostname or "(unknown)"
        # Windows에서 psycopg async + ProactorEventLoop 충돌이 발생할 수 있어
        # 비동기 init_db()는 실패해도 서버 기동을 막지 않는다.
        try:
            await init_db()
        except Exception as e:
            logger.warning("비동기 init_db 스킵: %s", e)
        logger.info(
            "Neon PostgreSQL 연결 완료 (host=%s). "
            "콘솔 Tables 가 비어 있으면 backend/.env 의 DATABASE_URL 이 "
            "Neon 대시보드 Connection string 과 같은지 확인하세요.",
            host,
        )
    except RuntimeError as e:
        logger.warning("DB 초기화 스킵: %s", e)
    yield


app = FastAPI(title="Whoareryu Main Page", lifespan=lifespan)
if _AUTH_AVAILABLE:
    app.include_router(auth_router)
app.include_router(weather_router)
app.include_router(secom_router)
app.include_router(gourmet_router)
app.include_router(titanic_router)


def _gemini_error_detail(exc: Exception) -> tuple[int, str]:
    """Gemini API 오류를 HTTP 상태·사용자 메시지로 변환."""
    msg = str(exc)
    upper = msg.upper()
    if "API_KEY_INVALID" in upper or "API KEY NOT FOUND" in upper:
        return (
            503,
            "GEMINI_API_KEY가 유효하지 않습니다. backend/.env 에 Google AI Studio에서 발급한 키를 넣고 서버를 재시작하세요.",
        )
    if "PERMISSION_DENIED" in upper or "403" in msg:
        return 503, "Gemini API 권한이 없습니다. API 키와 프로젝트 설정을 확인하세요."
    if "QUOTA" in upper or "RESOURCE_EXHAUSTED" in upper:
        return 503, "Gemini API 할당량이 초과되었습니다. 잠시 후 다시 시도하세요."
    return 502, msg


def _messages_to_gemini_contents(messages: list[ChatMessage]) -> list[dict]:
    out: list[dict] = []
    for m in messages:
        role = "model" if m.role == "assistant" else "user"
        text = m.content.strip()
        if not text:
            raise HTTPException(status_code=422, detail="빈 content는 허용되지 않습니다.")
        out.append({"role": role, "parts": [text]})
    return out


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning("요청 검증 오류: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "요청 검증 오류",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, (HTTPException, StarletteHTTPException)):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "message": exc.detail},
        )
    logger.exception("처리되지 않은 오류 (%s): %s", type(exc).__name__, exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": str(exc),
            "type": type(exc).__name__,
        },
    )


async def get_db_health_adapter(
    db: AsyncSession = Depends(get_db),
) -> SqlAlchemyDbHealthAdapter:
    return SqlAlchemyDbHealthAdapter(db)


@app.get("/")
def read_root():
    return {"message": "FastAPI 메인 페이지.", "docs": "/docs"}


@app.post("/chat")
def chat(body: ChatRequest):
    """JSON 메시지 목록으로 Gemini에 질의하고, 응답 텍스트를 반환합니다."""
    if body.messages[-1].role != "user":
        raise HTTPException(
            status_code=422,
            detail="messages의 마지막 요소는 role=user 여야 합니다.",
        )
    if keymaker is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini(메트릭스) 모듈이 비활성화되어 있습니다.",
        )
    try:
        gemini = keymaker.generative_model(body.model)
        model_used = keymaker.resolve_model_name(body.model or keymaker.gemini_model_name)
    except MissingGeminiKeyError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    contents = _messages_to_gemini_contents(body.messages)
    try:
        response = gemini.generate_content(contents)
    except Exception as e:
        logger.exception("Gemini generate_content 실패")
        status, detail = _gemini_error_detail(e)
        raise HTTPException(status_code=status, detail=detail) from e

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise HTTPException(
            status_code=502,
            detail="모델이 텍스트 응답을 반환하지 않았습니다.",
        )
    return {"text": text, "model": model_used}


@app.get("/db-check")
async def check_db(
    db_health: SqlAlchemyDbHealthAdapter = Depends(get_db_health_adapter),
):
    """Neon 등 DB 연결 확인. SQL 실패 시에도 HTTP 200 + status=error 본문."""
    return await db_health.check_sql_time()


@app.get("/doro/data")
def read_doro_data():
    if DoroDirector is None:
        raise HTTPException(status_code=503, detail="Doro 모듈이 비활성화되어 있습니다.")
    doro = DoroDirector()
    df = doro.get_data()
    return df.to_dict(orient="records")

#회원가입
@app.post("/signup", response_model=UserPublic, status_code=201, tags=["회원가입"])
async def signup_member(body: SignupRequest, db: AsyncSession = Depends(get_sync_db)):
    """회원가입 — localhost:3000 → Neon `users` 단일 테이블."""
    auth_db_unavailable()
    logger.info(
        "[main] 회원가입 요청 — username=%s email=%s nickname=%s",
        body.username,
        body.email,
        body.nickname,
    )
    return auth_signup(body, db)


@app.post("/login", response_model=UserPublic, tags=["로그인"])
async def login_member(body: LoginRequest, db: AsyncSession = Depends(get_sync_db)):
    """로그인 — users 테이블 검증 + last_login_at 갱신."""
    auth_db_unavailable()
    logger.info("[main] 로그인 요청 — username=%s", body.username)
    return auth_login(body, db)


if __name__ == "__main__":
    import uvicorn

    # reload 시 자식 프로세스도 WindowsSelectorEventLoopPolicy 유지
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        loop="asyncio",
    )




