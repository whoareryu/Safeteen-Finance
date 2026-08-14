from __future__ import annotations

from safeteen.app.dtos.emergency_dto import EmergencyGuideCommand, EmergencyGuideResult
from safeteen.app.ports.output.emergency_guide_repository import EmergencyGuideRepository
from safeteen.app.use_cases.emergency_guide_interactor import EmergencyGuideInteractor


class _FakeEmergencyGuideRepository(EmergencyGuideRepository):
    def __init__(self, result: EmergencyGuideResult) -> None:
        self._result = result

    def get_guide(self) -> EmergencyGuideResult:
        return self._result


def test_get_guide_delegates_to_repository() -> None:
    expected = EmergencyGuideResult(account_freeze_steps=[], police_report_steps=[], hotlines=[])
    interactor = EmergencyGuideInteractor(repository=_FakeEmergencyGuideRepository(expected))

    result = interactor.get_guide(EmergencyGuideCommand(situation="계좌에서 돈이 빠져나갔어요"))

    assert result is expected
