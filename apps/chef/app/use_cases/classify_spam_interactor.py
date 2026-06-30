from __future__ import annotations

import json
import re

from chef.app.dtos.spam_dto import SpamClassificationCommand, SpamClassificationResult
from chef.app.ports.input.spam_use_case import SpamUseCase
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

from ontology.domain.spam.spam_category import SpamCategory
from ontology.domain.spam.spam_rules import match
from ontology.domain.spam.spam_taxonomy import TAXONOMY

_RULE_CONFIDENCE_THRESHOLD = 0.6


class ClassifySpamInteractor(SpamUseCase):
    def __init__(self, llm: T1MidFakerOrchestrator) -> None:
        self._llm = llm

    async def classify(self, cmd: SpamClassificationCommand) -> SpamClassificationResult:
        rule_match = match(cmd.subject, cmd.body)
        if rule_match.confidence >= _RULE_CONFIDENCE_THRESHOLD:
            return self._from_rule(rule_match)
        return await self._from_llm(cmd)

    def _from_rule(self, rule_match) -> SpamClassificationResult:
        node = TAXONOMY[rule_match.category]
        return SpamClassificationResult(
            category=rule_match.category.value,
            label=node.label,
            confidence=rule_match.confidence,
            is_spam=rule_match.category != SpamCategory.HAM,
            reason=f"키워드 매칭: {', '.join(rule_match.matched_keywords)}",
        )

    async def _from_llm(self, cmd: SpamClassificationCommand) -> SpamClassificationResult:
        taxonomy_context = "\n".join(
            f"- {node.category.value} ({node.label}): {node.description}"
            for node in TAXONOMY.values()
        )
        system = (
            "당신은 이메일 스팸 분류 전문가입니다.\n"
            f"다음 분류 체계를 사용하세요:\n{taxonomy_context}\n\n"
            "반드시 아래 JSON 형식으로만 응답하세요:\n"
            '{"category": "<category_value>", "confidence": <0.0~1.0>, "reason": "<이유>"}'
        )
        user = f"제목: {cmd.subject}\n발신자: {cmd.sender or '알 수 없음'}\n본문:\n{cmd.body}"
        raw = await self._llm.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ])
        return self._parse_llm(raw)

    def _parse_llm(self, raw: str) -> SpamClassificationResult:
        try:
            m = re.search(r'\{[^{}]*"category"[^{}]*\}', raw, re.DOTALL)
            data = json.loads(m.group() if m else raw)
            category = SpamCategory(data.get("category", "ham"))
            node = TAXONOMY[category]
            return SpamClassificationResult(
                category=category.value,
                label=node.label,
                confidence=float(data.get("confidence", 0.5)),
                is_spam=category != SpamCategory.HAM,
                reason=str(data.get("reason", "")),
            )
        except Exception:
            return SpamClassificationResult(
                category=SpamCategory.HAM.value,
                label=TAXONOMY[SpamCategory.HAM].label,
                confidence=0.0,
                is_spam=False,
                reason="분류 실패 — 정상 처리",
            )
