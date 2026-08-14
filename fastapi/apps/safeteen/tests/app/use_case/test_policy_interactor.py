from __future__ import annotations

from safeteen.app.ports.output.policy_repository import PolicyRepository
from safeteen.app.use_cases.policy_interactor import PolicyInteractor
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


class _FakePolicyRepository(PolicyRepository):
    def __init__(self, policies: list[AlternativePolicy]) -> None:
        self._policies = policies

    async def list_all(self) -> list[AlternativePolicy]:
        return self._policies


async def test_list_policies_delegates_to_repository() -> None:
    expected = [AlternativePolicy(title="햇살론 유스", description="설명", official_link="https://example.com")]
    interactor = PolicyInteractor(repository=_FakePolicyRepository(expected))

    result = await interactor.list_policies()

    assert result == expected
