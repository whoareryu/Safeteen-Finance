from __future__ import annotations

from ontology.app.dtos.dispatch_dto import DispatchRequestDto, DispatchResultDto
from ontology.app.dtos.maestro_dto import MaestroQueryDto, MaestroResultDto
from ontology.app.dtos.sommelier_dto import GraphQueryDto
from ontology.app.dtos.lens_dto import LensQueryDto
from ontology.app.ports.input.maestro_router_use_case import MaestroUseCase
from ontology.app.ports.input.sommelier_graph_use_case import SommelierUseCase
from ontology.app.ports.input.lens_search_use_case import LensUseCase
from ontology.app.ports.output.task_dispatch_port import TaskDispatchPort
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

_GRAPH_SIGNALS = ["관계", "연결", "이웃", "경로", "링크"]
_DEFAULT_COLLECTION = "knowledge"

_TASK_SIGNALS: dict[str, list[str]] = {
    "email":          ["이메일", "메일", "email", "메시지 보내", "편지"],
    "spam_classify":  ["스팸", "spam", "스팸 분류", "광고메일 확인"],
    "telegram":       ["텔레그램", "telegram"],
}


class MaestroInteractor(MaestroUseCase):
    def __init__(
        self,
        sommelier: SommelierUseCase,
        lens: LensUseCase,
        llm: T1MidFakerOrchestrator,
        dispatcher: TaskDispatchPort | None = None,
    ) -> None:
        self._sommelier = sommelier
        self._lens = lens
        self._llm = llm
        self._dispatcher = dispatcher

    # ── 지식 쿼리 라우팅 ─────────────────────────────────────────────────
    async def route(self, dto: MaestroQueryDto) -> MaestroResultDto:
        if any(sig in dto.question for sig in _GRAPH_SIGNALS):
            return await self._via_sommelier(dto.question)
        return await self._via_lens(dto.question)

    async def _via_sommelier(self, question: str) -> MaestroResultDto:
        cypher = "MATCH (n) WHERE n.name CONTAINS $keyword RETURN n LIMIT 5"
        result = await self._sommelier.query(
            GraphQueryDto(cypher=cypher, params={"keyword": question[:20]})
        )
        answer = await self._llm.chat([
            {"role": "system", "content": "지식 그래프 결과를 바탕으로 간결하게 답변하세요."},
            {"role": "user", "content": f"질문: {question}\n그래프 결과: {result.records}"},
        ])
        return MaestroResultDto(answer=answer, source="sommelier", context=result.records)

    async def _via_lens(self, question: str) -> MaestroResultDto:
        result = await self._lens.search(
            LensQueryDto(query=question, collection=_DEFAULT_COLLECTION)
        )
        answer = await self._llm.chat([
            {"role": "system", "content": "컨텍스트 검색 결과를 바탕으로 간결하게 답변하세요."},
            {"role": "user", "content": f"질문: {question}\n검색 결과: {result.hits}"},
        ])
        return MaestroResultDto(answer=answer, source="lens", context=result.hits)

    # ── 태스크 디스패치 ──────────────────────────────────────────────────
    async def dispatch(self, dto: DispatchRequestDto) -> DispatchResultDto:
        task_type = self._classify_task(dto.task)
        if self._dispatcher is None:
            return DispatchResultDto(
                task_type=task_type,
                routed_to="none",
                result={"error": "dispatcher가 등록되지 않았습니다"},
            )
        result = await self._dispatcher.dispatch(task_type, dto.payload)
        return DispatchResultDto(task_type=task_type, routed_to="chef", result=result)

    def _classify_task(self, task: str) -> str:
        task_lower = task.lower()
        for task_type, signals in _TASK_SIGNALS.items():
            if any(sig in task_lower for sig in signals):
                return task_type
        return "email"  # 기본값
