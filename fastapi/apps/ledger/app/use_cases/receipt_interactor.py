from __future__ import annotations

from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

from ledger.app.dtos.receipt_dto import ReceiptItemResult, ReceiptResult, ReceiptUploadCommand
from ledger.app.ports.input.receipt_use_case import ReceiptUseCase
from ledger.app.ports.output.receipt_repository import ReceiptRepository
from ledger.app.ports.output.receipt_vision_parser_port import ReceiptVisionParserPort
from ledger.domain.entities.receipt_entity import ReceiptEntity, ReceiptItemEntity


class ReceiptInteractor(ReceiptUseCase):

    def __init__(
        self,
        receipt_repository: ReceiptRepository,
        vision_parser: ReceiptVisionParserPort,
        storage: ImageStorageGateway,
    ) -> None:
        self._receipt_repository = receipt_repository
        self._vision_parser = vision_parser
        self._storage = storage

    async def upload(self, command: ReceiptUploadCommand) -> ReceiptResult:
        image_url = await self._storage.save(command.filename, command.content_type, command.data)
        extraction = await self._vision_parser.parse(command.data, command.content_type)

        record = await self._receipt_repository.save(
            ReceiptEntity(
                id=None,
                owner_user_id=command.owner_user_id,
                image_url=image_url,
                store_name=extraction.store_name,
                purchase_date=extraction.purchase_date,
                total_amount=extraction.total_amount,
                category=extraction.category,
                items=[
                    ReceiptItemEntity(
                        id=None,
                        name=item.name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        amount=item.amount,
                    )
                    for item in extraction.items
                ],
            )
        )
        return await self._to_result(record)

    async def list_by_owner(self, owner_user_id: int) -> list[ReceiptResult]:
        records = await self._receipt_repository.list_by_owner(owner_user_id)
        return [await self._to_result(record) for record in records]

    async def get(self, receipt_id: int) -> ReceiptResult:
        record = await self._receipt_repository.get(receipt_id)
        return await self._to_result(record)

    async def _to_result(self, record: ReceiptEntity) -> ReceiptResult:
        # DB에는 save()가 준 원래 URL을 저장해 두고, 응답을 내려줄 때마다 매번
        # 새로 서명한(퍼블릭 접근 불가 버킷에서도 열리는) URL로 바꿔서 돌려준다.
        viewable_url = await self._storage.presigned_url(record.image_url)
        return ReceiptResult(
            id=record.id,  # type: ignore[arg-type]
            owner_user_id=record.owner_user_id,
            image_url=viewable_url,
            store_name=record.store_name,
            purchase_date=record.purchase_date,
            total_amount=record.total_amount,
            category=record.category,
            items=[
                ReceiptItemResult(
                    name=item.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    amount=item.amount,
                )
                for item in record.items
            ],
            created_at=record.created_at,  # type: ignore[arg-type]
        )
