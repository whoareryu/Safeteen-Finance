from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin

POLICY_EMBEDDING_DIM = 768


class PolicyDocumentORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "safeteen_policy_documents"

    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    official_link: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(POLICY_EMBEDDING_DIM), nullable=False)
