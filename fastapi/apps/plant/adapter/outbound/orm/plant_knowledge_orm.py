from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin

PLANT_KNOWLEDGE_EMBEDDING_DIM = 1024  # bge-m3 임베딩 차원


class PlantKnowledgeORM(IntIdPrimaryKeyMixin, Base):
    """RAG 지식 항목 — PlantDoc 질병 클래스(category=disease), house_plant_species 품종(category=species)."""

    __tablename__ = "plant_knowledge"

    category: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(PLANT_KNOWLEDGE_EMBEDDING_DIM), nullable=True
    )
