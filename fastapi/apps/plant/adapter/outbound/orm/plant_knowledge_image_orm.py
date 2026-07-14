from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class PlantKnowledgeImageORM(IntIdPrimaryKeyMixin, Base):
    """plant_knowledge에 딸린 원본 이미지 메타데이터.

    PlantDoc(YOLO)은 한 이미지에 bbox가 여러 개일 수 있어 1 row = 1 bbox.
    house_plant_species는 분류 데이터셋이라 bbox_*/split이 전부 NULL.
    """

    __tablename__ = "plant_knowledge_images"

    knowledge_id: Mapped[int] = mapped_column(ForeignKey("plant_knowledge.id"), nullable=False)
    image_filename: Mapped[str] = mapped_column(String, nullable=False)
    split: Mapped[str | None] = mapped_column(String(10), nullable=True)
    bbox_x_center: Mapped[float | None] = mapped_column(Float, nullable=True)
    bbox_y_center: Mapped[float | None] = mapped_column(Float, nullable=True)
    bbox_width: Mapped[float | None] = mapped_column(Float, nullable=True)
    bbox_height: Mapped[float | None] = mapped_column(Float, nullable=True)
