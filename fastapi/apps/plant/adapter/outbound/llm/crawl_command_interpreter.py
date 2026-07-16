from __future__ import annotations

import json

from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator
from plant.app.ports.output.crawl_command_interpreter_port import CrawlCommandInterpreterPort

_MODEL = "qwen2.5:1.5b-instruct"

_PROMPT = """너는 웹 크롤링/스크래핑 명령을 해석하는 비서야. 사용자의 자연어 명령에서
찾고 싶은 핵심 키워드와 탐색 깊이(depth)를 추출해서, 아래 JSON 형식으로만 응답해.
다른 설명이나 텍스트는 절대 붙이지 마.

{"keyword": "핵심 키워드", "depth": 0에서 5 사이 정수}

depth를 명령에서 알 수 없으면 2를 기본값으로 써.

[예시]
명령: "몬스테라 키우기 정보를 찾아줘"
응답: {"keyword": "몬스테라", "depth": 2}

명령: "선인장 관련 글을 깊이 3단계까지 탐색해서 모아줘"
응답: {"keyword": "선인장", "depth": 3}
"""


class QwenCrawlCommandInterpreter(CrawlCommandInterpreterPort):
    """PoC 단계라 QLoRA 파인튜닝 없이, 이미 서빙 중인 Qwen 1.5B에 파싱 전용
    시스템 프롬프트만 갈아 끼워 명령을 해석한다 (semantic-routing과 동일 패턴)."""

    def __init__(self, model: str = _MODEL) -> None:
        self._llm = T1MidFakerOrchestrator(model=model)

    async def interpret(self, command: str) -> tuple[str, int]:
        raw = await self._llm.chat([
            {"role": "system", "content": _PROMPT},
            {"role": "user", "content": command},
        ])
        try:
            data = json.loads(raw)
            keyword = str(data.get("keyword") or "").strip() or command.strip()
            depth = max(0, min(int(data.get("depth", 2)), 5))
            return keyword, depth
        except (json.JSONDecodeError, ValueError, TypeError):
            return command.strip(), 2
