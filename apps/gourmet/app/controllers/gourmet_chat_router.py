"""맛집 전용 Gemini 채팅 — DB 맥락 주입."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from apps.gourmet.app.schemas.catalog_schemas import GourmetChatRequest, GourmetChatResponse
from apps.gourmet.app.services.gourmet_chat_service import build_gourmet_context
from apps.matrix.app.keymaker import MissingGeminiKeyError, keymaker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gourmet", tags=["gourmet-chat"])


@router.post("/chat", response_model=GourmetChatResponse)
def gourmet_chat(
    body: GourmetChatRequest,
    db: Session = Depends(get_sync_db),
):
    """맛집 RAG — ``restaurant_id`` 또는 ``q`` 로 DB 맥락을 Gemini에 전달."""
    if not body.messages or body.messages[-1].role != "user":
        raise HTTPException(
            status_code=422,
            detail="messages 의 마지막은 role=user 여야 합니다.",
        )
    context = build_gourmet_context(
        db,
        restaurant_id=body.restaurant_id,
        q=body.q,
    )
    try:
        gemini = keymaker.generative_model(body.model)
        model_used = keymaker.resolve_model_name(
            body.model or keymaker.gemini_model_name
        )
    except MissingGeminiKeyError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    contents: list[dict] = [
        {"role": "user", "parts": [context]},
        {
            "role": "model",
            "parts": ["네, 제공된 맛집 데이터만 근거로 답변하겠습니다."],
        },
    ]
    for m in body.messages:
        role = "model" if m.role == "assistant" else "user"
        text = (m.content or "").strip()
        if not text:
            raise HTTPException(status_code=422, detail="빈 content 는 허용되지 않습니다.")
        contents.append({"role": role, "parts": [text]})

    try:
        response = gemini.generate_content(contents)
    except Exception as e:
        logger.exception("[gourmet] chat Gemini 실패")
        raise HTTPException(status_code=502, detail=str(e)) from e

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise HTTPException(status_code=502, detail="모델이 텍스트 응답을 반환하지 않았습니다.")

    return GourmetChatResponse(
        text=text,
        model=model_used,
        context_summary=context[:500] + ("…" if len(context) > 500 else ""),
    )
