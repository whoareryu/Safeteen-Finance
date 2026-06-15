from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_james_director_dto import BookingCommand, JamesDirectorQuery, JamesDirectorResponse, PassengerCommand
from titanic.app.ports.output.crew_james_director_repository import JamesDirectorRepository

PersonCommand = PassengerCommand  # 내부 alias

logger = logging.getLogger(__name__)

_INSERT_BATCH_SIZE = 500


class JamesDirectorPGRepository(JamesDirectorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def receive_uploaded_records(
        self,
        person_commands: list[PersonCommand],
        booking_commands: list[BookingCommand],
    ) -> int:
        from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerORM  # noqa: PLC0415
        from titanic.adapter.outbound.orm.passenger_rose_model_orm import RoseModelORM  # noqa: PLC0415

        if len(person_commands) != len(booking_commands):
            raise ValueError(
                f"PersonCommand({len(person_commands)})와 BookingCommand({len(booking_commands)}) 개수가 다릅니다."
            )
        if not person_commands:
            return 0

        # 이미 존재하는 passenger_id 조회
        all_ids = [p.passenger_id for p in person_commands]
        existing = set(
            row[0]
            for row in (
                await self.session.execute(
                    select(JackTrainerORM.passenger_id).where(
                        JackTrainerORM.passenger_id.in_(all_ids)
                    )
                )
            ).all()
        )

        # 신규 데이터만 필터링
        new_pairs = [
            (p, b)
            for p, b in zip(person_commands, booking_commands, strict=True)
            if p.passenger_id not in existing
        ]

        if not new_pairs:
            logger.info("[James Repository] 신규 데이터 없음 — 전부 중복")
            return 0

        inserted = 0
        for batch_start in range(0, len(new_pairs), _INSERT_BATCH_SIZE):
            batch = new_pairs[batch_start : batch_start + _INSERT_BATCH_SIZE]
            batch_person = [p for p, _ in batch]
            batch_booking = [b for _, b in batch]

            await self.session.execute(
                pg_insert(JackTrainerORM).values([
                    dict(
                        passenger_id=p.passenger_id,
                        name=p.name,
                        gender=p.gender,
                        age=p.age,
                        sib_sp=p.sib_sp,
                        parch=p.parch,
                        survived=p.survived,
                    )
                    for p in batch_person
                ]).on_conflict_do_nothing(index_elements=["passenger_id"])
            )

            await self.session.execute(
                pg_insert(RoseModelORM).values([
                    dict(
                        passenger_id=p.passenger_id,
                        pclass=b.pclass,
                        ticket=b.ticket,
                        fare=b.fare,
                        cabin=b.cabin,
                        embarked=b.embarked,
                    )
                    for p, b in zip(batch_person, batch_booking, strict=True)
                ]).on_conflict_do_nothing()
            )

            inserted += len(batch)

        logger.info("[James Repository] INSERT 완료: %d건 (중복 제외)", inserted)
        return inserted

    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        return JamesDirectorResponse(answer=f"id={query.id * 10000}, name={query.name}")
