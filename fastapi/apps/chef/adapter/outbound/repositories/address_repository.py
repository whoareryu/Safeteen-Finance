from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chef.adapter.outbound.orm.address_orm import ContactORM
from chef.app.dtos.address_dto import (
    AddressCreateCommand,
    AddressDetailResult,
    AddressUploadResult,
    ContactUploadDto,
)
from chef.app.ports.output.address_port import AddressPort

logger = logging.getLogger(__name__)


class AddressRepository(AddressPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_contact(self, cmd: AddressCreateCommand) -> AddressDetailResult:
        row = ContactORM(
            id=str(uuid.uuid4()),
            user_id=cmd.user_id,
            first_name=cmd.name,
            email=cmd.email,
            phone=cmd.phone or "",
            company=cmd.company or "",
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_result(row)

    async def list_contacts(self) -> list[AddressDetailResult]:
        result = await self._session.execute(select(ContactORM))
        return [_to_result(r) for r in result.scalars().all()]

    async def upload_contacts(self, rows: list[ContactUploadDto]) -> AddressUploadResult:
        valid = [r for r in rows if r.email_1_value and "@" in r.email_1_value]
        if not valid:
            return AddressUploadResult(saved=0)

        incoming_emails = [r.email_1_value for r in valid]
        existing = await self._session.execute(
            select(ContactORM.email).where(ContactORM.email.in_(incoming_emails))
        )
        existing_emails = {row[0] for row in existing}

        new_rows = [r for r in valid if r.email_1_value not in existing_emails]
        for r in new_rows:
            self._session.add(ContactORM(
                id=str(uuid.uuid4()),
                user_id=0,
                first_name=r.first_name or "",
                last_name=r.last_name or "",
                middle_name=r.middle_name or "",
                nickname=r.nickname or "",
                email=r.email_1_value,
                phone=r.phone_1_value or "",
                company=r.organization_name or "",
                company_title=r.organization_title or "",
                birthday=r.birthday or "",
                notes=r.notes or "",
                labels=r.labels or "",
            ))

        await self._session.commit()
        logger.info(
            "주소록 업로드: 유효 %d건 중 신규 %d건 저장 (중복 %d건 건너뜀)",
            len(valid), len(new_rows), len(existing_emails),
        )
        return AddressUploadResult(saved=len(new_rows))


def _to_result(row: ContactORM) -> AddressDetailResult:
    name_parts = [p for p in (row.first_name, row.last_name) if p]
    return AddressDetailResult(
        id=0,
        name=" ".join(name_parts) if name_parts else row.email,
        email=row.email or "",
        company=row.company or "",
        phone=row.phone or "",
    )
