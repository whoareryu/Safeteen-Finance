from __future__ import annotations

from chef.app.ports.input.email_use_case import EmailUseCase
from ontology.app.ports.output.task_dispatch_port import TaskDispatchPort


class ChefTaskDispatcher(TaskDispatchPort):
    """chef 스포크의 유스케이스를 Maestro(hub)의 TaskDispatchPort로 노출한다."""

    def __init__(self, email: EmailUseCase) -> None:
        self._email = email

    async def dispatch(self, task_type: str, payload: dict) -> dict:
        return await self._handle_email(payload)

    async def _handle_email(self, payload: dict) -> dict:
        dto = await self._email.execute(
            to=payload["to"],
            prompt=payload.get("prompt", ""),
        )
        return {"to": dto.to, "subject": dto.subject, "body": dto.body, "status": "sent"}
