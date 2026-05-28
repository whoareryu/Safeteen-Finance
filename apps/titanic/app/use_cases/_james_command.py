import logging

from sqlalchemy.orm import Session

from apps.titanic.app.use_cases.train_use_case import (
    augment_user_message_with_context,
    build_titanic_chat_context,
)
from apps.titanic.app.use_cases.titanic_gemini import generate_chat_text
from apps.titanic.app.use_cases.titanic_schemas import ChatMessage, ChatRequest

logger = logging.getLogger(__name__)


class TitanicCommandUseCase:
    def chat(self, body: ChatRequest, db: Session) -> dict:
        context = build_titanic_chat_context(db)
        msgs = list(body.messages)
        last = msgs[-1]
        msgs[-1] = ChatMessage(
            role="user",
            content=augment_user_message_with_context(last.content, context),
        )
        text, model_used = generate_chat_text(msgs, body.model)
        return {
            "text": text,
            "model": model_used,
            "context_source": "db" if "PostgreSQL" in context else "none",
        }
