from __future__ import annotations

import json
import logging
import re

from chef.app.dtos.email_dto import EmailTaskDto
from chef.app.ports.input.email_use_case import EmailUseCase
from chef.app.ports.output.email_gateway import EmailGateway
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator
from ontology.app.dtos.maestro_dto import MaestroQueryDto
from ontology.app.ports.input.maestro_router_use_case import MaestroUseCase

logger = logging.getLogger(__name__)

_BASE_SYSTEM = (
    "당신은 이메일 작성 전문가입니다. "
    "반드시 아래 JSON 형식으로만 응답하세요. 마크다운 코드블록(```)이나 다른 텍스트는 절대 포함하지 마세요.\n"
    '{"subject": "이메일 제목", "body": "이메일 본문"}'
)


class EmailInteractor(EmailUseCase):
    def __init__(
        self,
        llm: T1MidFakerOrchestrator,
        gateway: EmailGateway,
        maestro: MaestroUseCase,
    ) -> None:
        self._llm = llm
        self._gateway = gateway
        self._maestro = maestro

    async def execute(self, to: str, prompt: str) -> EmailTaskDto:
        subject, body = await self._generate(prompt)
        dto = EmailTaskDto(to=to, subject=subject, body=body)
        await self._gateway.send(dto)
        return dto

    async def _generate(self, prompt: str) -> tuple[str, str]:
        system = await self._build_system(prompt)
        raw = await self._llm.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ])
        return _parse(raw)

    async def _build_system(self, prompt: str) -> str:
        try:
            guidance = await self._maestro.route(MaestroQueryDto(question=prompt))
            if guidance.answer:
                return f"{_BASE_SYSTEM}\n\n온톨로지 작성 지침:\n{guidance.answer}"
        except Exception:
            logger.warning("Maestro 지침 조회 실패 — 기본 프롬프트로 진행")
        return _BASE_SYSTEM


def _parse(raw: str) -> tuple[str, str]:
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    try:
        m = re.search(r"\{.+\}", cleaned, re.DOTALL)
        data = json.loads(m.group() if m else cleaned)
        return str(data["subject"]), str(data["body"])
    except Exception:
        lines = cleaned.splitlines()
        subject = lines[0].strip() if lines else "이메일"
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else cleaned
        return subject, body
