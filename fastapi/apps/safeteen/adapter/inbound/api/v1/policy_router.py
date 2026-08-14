from __future__ import annotations

from fastapi import APIRouter, Depends

from safeteen.adapter.inbound.api.schemas.policy_schema import PolicyResponse
from safeteen.adapter.inbound.mappers.policy_mapper import to_response
from safeteen.app.ports.input.policy_use_case import PolicyUseCase
from safeteen.dependencies.policy_provider import get_policy_use_case

policy_router = APIRouter(tags=["safeteen-policies"])


@policy_router.get("/policies", summary="청년 대상 합법 금융 지원 정책 목록 조회")
async def list_policies(
    use_case: PolicyUseCase = Depends(get_policy_use_case),
) -> list[PolicyResponse]:
    return [to_response(policy) for policy in await use_case.list_policies()]
