from __future__ import annotations

from admin.app.dtos.pdf_loader_dto import PdfSummaryResult, PdfUploadCommand
from admin.app.ports.input.pdf_loader_use_case import PdfLoaderUseCase
from admin.app.ports.output.pdf_loader_repository import PdfLoaderRepository
from admin.app.ports.output.pdf_summary_generator_port import PdfSummaryGeneratorPort
from admin.app.ports.output.pdf_text_extractor_port import PdfTextExtractorPort
from admin.domain.entities.pdf_document_entity import PdfDocumentEntity


class PdfLoaderInteractor(PdfLoaderUseCase):

    def __init__(
        self,
        extractor: PdfTextExtractorPort,
        generator: PdfSummaryGeneratorPort,
        repository: PdfLoaderRepository,
    ) -> None:
        self._extractor = extractor
        self._generator = generator
        self._repository = repository

    async def summarize(self, command: PdfUploadCommand) -> PdfSummaryResult:
        extracted_text = await self._extractor.extract(command.filename, command.data)
        summary = await self._generator.summarize(extracted_text)

        record = await self._repository.save(
            PdfDocumentEntity(
                id=None,
                filename=command.filename,
                extracted_text=extracted_text,
                summary=summary,
            )
        )
        return self._to_result(record)

    async def get(self, document_id: int) -> PdfSummaryResult:
        record = await self._repository.get(document_id)
        return self._to_result(record)

    @staticmethod
    def _to_result(record: PdfDocumentEntity) -> PdfSummaryResult:
        return PdfSummaryResult(
            id=record.id,  # type: ignore[arg-type]
            filename=record.filename,
            extracted_text=record.extracted_text,
            summary=record.summary,
        )
