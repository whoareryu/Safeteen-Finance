from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from admin.adapter.outbound.client.pdf_summary_generator_client import PdfSummaryGeneratorClient
from admin.adapter.outbound.client.pdf_text_extractor_client import PdfTextExtractorClient
from admin.adapter.outbound.repositories.pdf_loader_pg_repository import PdfLoaderPgRepository
from admin.app.ports.input.pdf_loader_use_case import PdfLoaderUseCase
from admin.app.use_cases.pdf_loader_interactor import PdfLoaderInteractor
from apps.database import get_db


def get_pdf_loader_use_case(db: AsyncSession = Depends(get_db)) -> PdfLoaderUseCase:
    return PdfLoaderInteractor(
        extractor=PdfTextExtractorClient(),
        generator=PdfSummaryGeneratorClient(),
        repository=PdfLoaderPgRepository(session=db),
    )
