from __future__ import annotations

from safeteen.adapter.outbound.orm.policy_document_orm import PolicyDocumentORM
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


def to_entity(orm: PolicyDocumentORM) -> AlternativePolicy:
    return AlternativePolicy(
        title=orm.title,
        description=orm.description,
        official_link=orm.official_link,
    )


def to_orm(policy: AlternativePolicy, embedding: list[float]) -> PolicyDocumentORM:
    return PolicyDocumentORM(
        title=policy.title,
        description=policy.description,
        official_link=policy.official_link,
        embedding=embedding,
    )
