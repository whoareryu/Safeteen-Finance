from __future__ import annotations

from safeteen.app.ports.input.policy_use_case import PolicyUseCase
from safeteen.app.ports.output.policy_repository import PolicyRepository
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


class PolicyInteractor(PolicyUseCase):

    def __init__(self, repository: PolicyRepository) -> None:
        self._repository = repository

    async def list_policies(self) -> list[AlternativePolicy]:
        return await self._repository.list_all()
