"""맛집 전용 채팅 — DB 맥락 + ExaOne."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from restaurant.adapter.inbound.api.schemas.catalog_schema import GourmetChatRequest, GourmetChatResponse
from restaurant.app.use_cases.gourmet_chat_interactor import build_gourmet_context
from core.matrix.vault_keymaker_secret_manager import keymaker
from core.lol.t1_mid_faker_orchestrator import _MODEL as FAKER_MODEL

router = APIRouter(prefix="/gourmet", tags=["gourmet-chat"])


@router.post("/chat", response_model=GourmetChatResponse)
async def gourmet_chat(
    body: GourmetChatRequest,
    db: Session = Depends(get_sync_db),
):
    """맛집 RAG — ``restaurant_id`` 또는 ``q`` 로 DB 맥락을 ExaOne에 전달."""
    context = build_gourmet_context(
        db,
        restaurant_id=body.restaurant_id,
        q=body.q,
    )

    contents: list[dict] = [
        {"role": "user", "parts": [{"text": context}]},
        {
            "role": "model",
            "parts": [{"text": "네, 제공된 맛집 데이터만 근거로 답변하겠습니다."}],
        },
    ]
    for m in body.messages:
        role = "model" if m.role == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": (m.content or "").strip()}]})

    text = await keymaker.generate_content(contents)
    return GourmetChatResponse(
        text=text,
        model=FAKER_MODEL,
        context_summary=context[:500] + ("…" if len(context) > 500 else ""),
    )
