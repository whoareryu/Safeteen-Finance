from __future__ import annotations

import ollama
from qdrant_client import AsyncQdrantClient

from ontology.app.ports.output.lens_search_port import LensPort

_EMBED_MODEL = "nomic-embed-text"


class LensRepository(LensPort):
    def __init__(self, host: str, port: int) -> None:
        self._qdrant = AsyncQdrantClient(host=host, port=port)
        self._ollama = ollama.AsyncClient()

    async def embed(self, text: str) -> list[float]:
        response = await self._ollama.embed(model=_EMBED_MODEL, input=text)
        return response.embeddings[0]

    async def search_by_vector(
        self, collection: str, vector: list[float], limit: int
    ) -> list[dict]:
        results = await self._qdrant.search(
            collection_name=collection, query_vector=vector, limit=limit
        )
        return [{"score": r.score, "payload": r.payload} for r in results]
