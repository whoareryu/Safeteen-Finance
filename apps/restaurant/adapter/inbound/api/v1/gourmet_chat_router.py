"""맛집 전용 Gemini 채팅 — DB 맥락 주입."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from restaurant.adapter.inbound.api.schemas.catalog_schema import GourmetChatRequest, GourmetChatResponse
from restaurant.app.use_cases.gourmet_chat_interactor import build_gourmet_context
from core.matrix.vault_keymaker_secret_manager import keymaker

router = APIRouter(prefix="/gourmet", tags=["gourmet-chat"])


@router.post("/chat", response_model=GourmetChatResponse)
def gourmet_chat(
    body: GourmetChatRequest,
    db: Session = Depends(get_sync_db),
):
    """맛집 RAG — ``restaurant_id`` 또는 ``q`` 로 DB 맥락을 Gemini에 전달."""
    context = build_gourmet_context(
        db,
        restaurant_id=body.restaurant_id,
        q=body.q,
    )
    gemini = keymaker.generative_model(body.model)
    model_used = keymaker.resolve_model_name(
        body.model or keymaker.gemini_model_name
    )
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
        contents.append({"role": role, "parts": [text]})

    response = gemini.generate_content(contents)
    text = (getattr(response, "text", None) or "").strip()
    return GourmetChatResponse(
        text=text,
        model=model_used,
        context_summary=context[:500] + ("…" if len(context) > 500 else ""),
    )
