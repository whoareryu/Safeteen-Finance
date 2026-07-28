from __future__ import annotations

from abc import ABC, abstractmethod

from admin.domain.entities.pdf_document_entity import PdfDocumentEntity


class PdfLoaderRepository(ABC):

    @abstractmethod
    async def save(self, entity: PdfDocumentEntity) -> PdfDocumentEntity:
        pass

    @abstractmethod
    async def get(self, document_id: int) -> PdfDocumentEntity:
        pass
