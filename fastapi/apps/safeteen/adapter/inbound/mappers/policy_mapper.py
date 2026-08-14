from __future__ import annotations

from safeteen.adapter.inbound.api.schemas.policy_schema import PolicyResponse
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


def to_response(policy: AlternativePolicy) -> PolicyResponse:
    return PolicyResponse(
        title=policy.title,
        description=policy.description,
        official_link=policy.official_link,
    )
