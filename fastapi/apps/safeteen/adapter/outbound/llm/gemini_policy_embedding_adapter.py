from __future__ import annotations

from google import genai
from google.genai import types

from core.infra.secret_manager import secret_manager

from safeteen.adapter.outbound.orm.policy_document_orm import POLICY_EMBEDDING_DIM
from safeteen.app.ports.output.policy_embedding_port import PolicyEmbeddingPort

_MODEL = "gemini-embedding-001"


class GeminiPolicyEmbeddingAdapter(PolicyEmbeddingPort):
    """Outbound 어댑터 — Gemini 임베딩 API로 정책 매칭용 RAG 벡터를 생성한다."""

    def __init__(self, api_key: str | None = None, model: str = _MODEL) -> None:
        resolved_key = api_key or secret_manager.get_secret("GEMINI_API_KEY")
        self._client = genai.Client(api_key=resolved_key)
        self._model = model

    async def embed(self, text: str) -> list[float]:
        response = await self._client.aio.models.embed_content(
            model=self._model,
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=POLICY_EMBEDDING_DIM),
        )
        if not response.embeddings or not response.embeddings[0].values:
            raise ValueError("Gemini가 임베딩 벡터를 반환하지 않았습니다.")
        return response.embeddings[0].values
