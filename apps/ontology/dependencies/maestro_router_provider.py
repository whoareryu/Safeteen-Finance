from __future__ import annotations

from typing import Callable

from ontology.app.ports.input.maestro_router_use_case import MaestroUseCase
from ontology.app.use_cases.maestro_router_interactor import MaestroInteractor
from ontology.dependencies.sommelier_graph_provider import get_sommelier_use_case
from ontology.dependencies.lens_search_provider import get_lens_use_case
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

# composition root(main.py)에서 등록하는 팩토리
_dispatch_factory: Callable[[], MaestroUseCase] | None = None


def register_dispatch_factory(factory: Callable[[], MaestroUseCase]) -> None:
    global _dispatch_factory
    _dispatch_factory = factory


def get_maestro_use_case() -> MaestroInteractor:
    return MaestroInteractor(
        sommelier=get_sommelier_use_case(),
        lens=get_lens_use_case(),
        llm=T1MidFakerOrchestrator(),
    )


def get_dispatch_maestro_use_case() -> MaestroUseCase:
    if _dispatch_factory is not None:
        return _dispatch_factory()
    return get_maestro_use_case()  # fallback: dispatcher 없이 동작
