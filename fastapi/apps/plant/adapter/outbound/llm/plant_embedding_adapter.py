from __future__ import annotations

import httpx

from core.matrix.secret_manager import secret_manager
from plant.app.ports.output.embedding_port import EmbeddingPort

_EMBEDDING_MODEL = "bge-m3"


class PlantEmbeddingAdapter(EmbeddingPort):
    """Ollama bge-m3 임베딩 어댑터 — RAG 쿼리 벡터 생성."""

    def __init__(self, model: str = _EMBEDDING_MODEL) -> None:
        self._model = model
        self._base_url = secret_manager.get_secret("OLLAMA_HOST", "http://host.docker.internal:11434")

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=30.0) as client:
            response = await client.post(
                "/api/embeddings", json={"model": self._model, "prompt": text}
            )
            response.raise_for_status()
            return response.json()["embedding"]
