from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from admin.adapter.outbound.mappers.pdf_document_orm_mapper import to_entity, to_orm
from admin.adapter.outbound.orm.pdf_document_orm import PdfDocumentORM
from admin.app.ports.output.pdf_loader_repository import PdfLoaderRepository
from admin.domain.entities.pdf_document_entity import PdfDocumentEntity


class PdfLoaderPgRepository(PdfLoaderRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entity: PdfDocumentEntity) -> PdfDocumentEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def get(self, document_id: int) -> PdfDocumentEntity:
        orm = await self.session.get(PdfDocumentORM, document_id)
        if orm is None:
            raise ValueError(f"Pdf document {document_id} not found")
        return to_entity(orm)
