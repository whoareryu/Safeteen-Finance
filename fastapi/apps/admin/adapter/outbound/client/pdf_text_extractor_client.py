from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

from neo4j_graphrag.experimental.components.pdf_loader import PdfLoader

from admin.app.ports.output.pdf_text_extractor_port import PdfTextExtractorPort


class PdfTextExtractorClient(PdfTextExtractorPort):
    """neo4j_graphrag PdfLoader(pypdf 기반)로 PDF 텍스트를 추출하는 어댑터."""

    def __init__(self) -> None:
        self._loader = PdfLoader()

    async def extract(self, filename: str, data: bytes) -> str:
        suffix = Path(filename).suffix or ".pdf"
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        try:
            await asyncio.to_thread(self._write_and_close, fd, data)
            document = await self._loader.run(filepath=Path(tmp_path))
            return document.text
        finally:
            await asyncio.to_thread(os.unlink, tmp_path)

    @staticmethod
    def _write_and_close(fd: int, data: bytes) -> None:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
