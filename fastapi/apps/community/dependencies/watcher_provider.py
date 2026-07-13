from community.adapter.outbound.guardrail.kc_electra_guardrail import get_kc_electra_guardrail
from community.app.ports.input.watcher_use_case import WatcherUseCase
from community.app.use_cases.watcher_interactor import WatcherInteractor


def get_watcher_use_case() -> WatcherUseCase:
    return WatcherInteractor(guardrail=get_kc_electra_guardrail())
