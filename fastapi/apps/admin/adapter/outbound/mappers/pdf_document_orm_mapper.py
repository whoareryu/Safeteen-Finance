from __future__ import annotations

from admin.adapter.outbound.orm.pdf_document_orm import PdfDocumentORM
from admin.domain.entities.pdf_document_entity import PdfDocumentEntity


def to_entity(orm: PdfDocumentORM) -> PdfDocumentEntity:
    return PdfDocumentEntity(
        id=orm.id,
        filename=orm.filename,
        extracted_text=orm.extracted_text,
        summary=orm.summary,
        created_at=orm.created_at,
    )


def to_orm(entity: PdfDocumentEntity) -> PdfDocumentORM:
    return PdfDocumentORM(
        filename=entity.filename,
        extracted_text=entity.extracted_text,
        summary=entity.summary,
    )
