from __future__ import annotations

from datetime import date, datetime

from ledger.app.dtos.receipt_dto import ReceiptUploadCommand
from ledger.app.ports.output.receipt_vision_parser_port import (
    ExtractedReceiptItem,
    ReceiptExtraction,
)
from ledger.app.use_cases.receipt_interactor import ReceiptInteractor
from ledger.domain.entities.receipt_entity import ReceiptEntity


class _FakeReceiptRepository:
    def __init__(self) -> None:
        self.saved: ReceiptEntity | None = None

    async def save(self, entity: ReceiptEntity) -> ReceiptEntity:
        self.saved = ReceiptEntity(
            id=99,
            owner_user_id=entity.owner_user_id,
            image_url=entity.image_url,
            store_name=entity.store_name,
            purchase_date=entity.purchase_date,
            total_amount=entity.total_amount,
            category=entity.category,
            items=entity.items,
            created_at=datetime(2026, 8, 4, 12, 0, 0),
        )
        return self.saved

    async def get(self, receipt_id: int) -> ReceiptEntity:
        assert self.saved is not None
        return self.saved

    async def list_by_owner(self, owner_user_id: int) -> list[ReceiptEntity]:
        return [self.saved] if self.saved else []


class _FakeVisionParser:
    def __init__(self, extraction: ReceiptExtraction) -> None:
        self._extraction = extraction

    async def parse(self, data: bytes, content_type: str) -> ReceiptExtraction:
        return self._extraction


class _FakeImageStorage:
    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        return f"https://fake-bucket/receipts/{filename}"


def _make_extraction() -> ReceiptExtraction:
    return ReceiptExtraction(
        store_name="이마트 역삼점",
        purchase_date=date(2026, 8, 3),
        total_amount=15400.0,
        category="식비",
        items=[
            ExtractedReceiptItem(name="우유", quantity=1, unit_price=2900.0, amount=2900.0),
            ExtractedReceiptItem(name="식빵", quantity=2, unit_price=3200.0, amount=6400.0),
        ],
    )


async def test_upload_saves_extracted_receipt_with_items():
    repository = _FakeReceiptRepository()
    interactor = ReceiptInteractor(
        receipt_repository=repository,
        vision_parser=_FakeVisionParser(_make_extraction()),
        storage=_FakeImageStorage(),
    )

    result = await interactor.upload(
        ReceiptUploadCommand(
            owner_user_id=1,
            filename="receipt.jpg",
            content_type="image/jpeg",
            data=b"fake-bytes",
        )
    )

    assert result.id == 99
    assert result.store_name == "이마트 역삼점"
    assert result.total_amount == 15400.0
    assert result.category == "식비"
    assert len(result.items) == 2
    assert result.items[0].name == "우유"
    assert result.image_url == "https://fake-bucket/receipts/receipt.jpg"


async def test_list_by_owner_returns_saved_receipts():
    repository = _FakeReceiptRepository()
    interactor = ReceiptInteractor(
        receipt_repository=repository,
        vision_parser=_FakeVisionParser(_make_extraction()),
        storage=_FakeImageStorage(),
    )
    await interactor.upload(
        ReceiptUploadCommand(
            owner_user_id=7,
            filename="a.jpg",
            content_type="image/jpeg",
            data=b"x",
        )
    )

    results = await interactor.list_by_owner(7)

    assert len(results) == 1
    assert results[0].owner_user_id == 7


async def test_get_returns_previously_saved_receipt():
    repository = _FakeReceiptRepository()
    interactor = ReceiptInteractor(
        receipt_repository=repository,
        vision_parser=_FakeVisionParser(_make_extraction()),
        storage=_FakeImageStorage(),
    )
    saved = await interactor.upload(
        ReceiptUploadCommand(
            owner_user_id=1,
            filename="a.jpg",
            content_type="image/jpeg",
            data=b"x",
        )
    )

    fetched = await interactor.get(saved.id)

    assert fetched.id == saved.id
    assert fetched.store_name == saved.store_name
