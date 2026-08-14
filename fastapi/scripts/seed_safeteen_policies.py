"""SafeTeen 청년 금융 지원 정책 시드 데이터 삽입 (RAG 벡터 매칭용).

이미 있는 title은 건너뛴다 (멱등).

사용:
  cd fastapi
  python scripts/seed_safeteen_policies.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent.parent
_apps_root = _backend_root / "apps"
for _path in (_backend_root, _apps_root):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from dotenv import load_dotenv

load_dotenv(_backend_root / ".env")

from sqlalchemy import select

from core.infra import database_manager as db_manager

from safeteen.adapter.outbound.llm.gemini_policy_embedding_adapter import GeminiPolicyEmbeddingAdapter
from safeteen.adapter.outbound.mappers.policy_document_orm_mapper import to_orm
from safeteen.adapter.outbound.orm.policy_document_orm import PolicyDocumentORM
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy

_POLICIES = [
    AlternativePolicy(
        title="햇살론 유스",
        description=(
            "만 34세 이하 사회초년생·대학(원)생을 위한 저금리 정책 서민금융상품. "
            "작업대출·내구제 대출·대포통장 명의대여 등 불법 사금융 대신 이용할 수 있다."
        ),
        official_link="https://www.kinfa.or.kr",
    ),
    AlternativePolicy(
        title="청년 긴급생계비 지원",
        description="실직·휴업·폐업 등으로 생계가 어려운 청년에게 소액 생계비를 무이자로 지원.",
        official_link="https://www.kinfa.or.kr",
    ),
    AlternativePolicy(
        title="청년 미소금융",
        description="저신용·저소득 청년의 창업·생계자금을 지원하는 미소금융중앙재단 상품.",
        official_link="https://www.smilemicrocredit.or.kr",
    ),
    AlternativePolicy(
        title="서민금융진흥원 청년 대상 상담",
        description="불법 사금융 피해가 의심될 때 무료로 대환·상담을 받을 수 있는 창구.",
        official_link="https://www.kinfa.or.kr",
    ),
]


async def main() -> None:
    db_manager.init_engine()
    if db_manager.async_session_maker is None:
        print("DB not initialized")
        sys.exit(1)

    embedder = GeminiPolicyEmbeddingAdapter()

    async with db_manager.async_session_maker() as db:
        for policy in _POLICIES:
            existing = await db.execute(
                select(PolicyDocumentORM.id).where(PolicyDocumentORM.title == policy.title)
            )
            if existing.scalar_one_or_none() is not None:
                print(f"SKIP (exists): {policy.title}")
                continue

            embedding = await embedder.embed(f"{policy.title} — {policy.description}")
            db.add(to_orm(policy, embedding))
            print(f"ADD: {policy.title}")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
