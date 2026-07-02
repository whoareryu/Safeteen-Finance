from __future__ import annotations

from chef.app.dtos.watcher_dto import ClassifyCommand, ClassifyResult, WatcherQuery, WatcherResponse
from chef.app.ports.input.watcher_use_case import WatcherUseCase
from chef.app.ports.output.guardrail_port import GuardrailPort


class WatcherInteractor(WatcherUseCase):
    def __init__(self, guardrail: GuardrailPort) -> None:
        self._guardrail = guardrail

    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse:
        return WatcherResponse(id=query.id, name=query.name)

    async def classify(self, cmd: ClassifyCommand) -> ClassifyResult:
        verdict = self._guardrail.score(cmd.text)
        return ClassifyResult(
            violates=verdict.violates,
            score=verdict.score,
            matched=verdict.matched,
            categories=verdict.categories,
            tokens=verdict.tokens,
        )
