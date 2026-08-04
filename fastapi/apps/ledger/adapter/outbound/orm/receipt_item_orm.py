from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class ReceiptItemORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "receipt_items"

    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
