from __future__ import annotations

from chef.app.dtos.spam_dto import SpamClassificationCommand
from chef.app.ports.input.email_use_case import EmailUseCase
from chef.app.ports.input.spam_use_case import SpamUseCase
from ontology.app.ports.output.task_dispatch_port import TaskDispatchPort


class ChefTaskDispatcher(TaskDispatchPort):
    """chef 스포크의 유스케이스를 Maestro(hub)의 TaskDispatchPort로 노출한다."""

    def __init__(self, email: EmailUseCase, spam: SpamUseCase) -> None:
        self._email = email
        self._spam = spam

    async def dispatch(self, task_type: str, payload: dict) -> dict:
        if task_type == "spam_classify":
            return await self._handle_spam(payload)
        return await self._handle_email(payload)

    async def _handle_email(self, payload: dict) -> dict:
        dto = await self._email.execute(
            to=payload["to"],
            prompt=payload.get("prompt", ""),
        )
        return {"to": dto.to, "subject": dto.subject, "body": dto.body, "status": "sent"}

    async def _handle_spam(self, payload: dict) -> dict:
        cmd = SpamClassificationCommand(
            subject=payload.get("subject", ""),
            body=payload.get("body", payload.get("prompt", "")),
            sender=payload.get("sender"),
        )
        result = await self._spam.classify(cmd)
        return {
            "category": result.category,
            "label": result.label,
            "confidence": result.confidence,
            "is_spam": result.is_spam,
            "reason": result.reason,
        }
