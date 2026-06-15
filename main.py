import os
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
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai

load_dotenv(_backend_root / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.db_health_adapter import DbHealthAdapter
from core.database import dispose_engine, get_db, init_db, init_engine

try:
    from doro.app.doro_director import DoroDirector
except ImportError:
    DoroDirector = None  # type: ignore[misc, assignment]

try:
    from titanic.app.james_controller import JamesController
except ImportError:
    JamesController = None  # type: ignore[misc, assignment]

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
GEMINI_MODEL = "gemini-1.5-flash"

_gemini_model: genai.GenerativeModel | None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
else:
    _gemini_model = None


class ChatRequest(BaseModel):
    """채팅 요청 본문. 사용자 메시지를 JSON으로 전달합니다."""

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
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from titanic.adapter.inbound.api import titanic_router  # noqa: E402

from restaurant.adapter.inbound.api import restaurant_router
from user.adapter.inbound.api import user_router

app.include_router(titanic_router, prefix="/api")
app.include_router(restaurant_router)
app.include_router(user_router)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FAST API 메인 페이지", "docs": "/docs"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    JSON 본문 `{"message": "..."}` 를 받아 Gemini 답변 문자열을 반환합니다.
    """
    if _gemini_model is None:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. backend/.env 에 키를 넣어 주세요.",
        )

    try:
        response = _gemini_model.generate_content(req.message)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini 호출 실패: {e!s}",
        ) from e

    try:
        text = (response.text or "").strip()
    except ValueError as e:
        feedback = getattr(response, "prompt_feedback", None)
        raise HTTPException(
            status_code=400,
            detail=f"응답 텍스트를 읽을 수 없습니다: {e!s}. prompt_feedback={feedback}",
        ) from e

    if not text:
        reason = None
        if getattr(response, "candidates", None):
            c0 = response.candidates[0]
            reason = getattr(c0, "finish_reason", None)
        raise HTTPException(
            status_code=502,
            detail=(
                "모델이 비어 있는 응답을 반환했습니다."
                + (f" (finish_reason={reason})" if reason else "")
            ),
        )

    return ChatResponse(reply=text)


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)