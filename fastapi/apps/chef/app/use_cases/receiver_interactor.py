from __future__ import annotations

import logging

from chef.app.dtos.receiver_dto import ReceiverCommand, ReceiverResult
from chef.app.ports.input.receiver_use_case import ReceiverUseCase
from chef.app.ports.output.guardrail_port import GuardrailPort
from chef.app.ports.output.receiver_port import ReceiverPort
from chef.domain.exceptions import PolicyViolationError

logger = logging.getLogger(__name__)


class ReceiverInteractor(ReceiverUseCase):
    def __init__(self, repository: ReceiverPort, guardrail: GuardrailPort) -> None:
        self._repo = repository
        self._guardrail = guardrail

    async def save(self, cmd: ReceiverCommand) -> ReceiverResult:
        verdict = self._guardrail.score(f"{cmd.subject} {cmd.preview}")
        if verdict.violates:
            logger.warning(
                "[ReceiverInteractor] 정책 위반 메일 차단 — sender=%s score=%.2f matched=%s",
                cmd.sender, verdict.score, verdict.matched,
            )
            raise PolicyViolationError(score=verdict.score, matched=verdict.matched)
        return await self._repo.save(cmd)
