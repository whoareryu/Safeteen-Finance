from __future__ import annotations

from datetime import date, datetime

from google import genai
from google.genai import types
from pydantic import BaseModel

from core.matrix.secret_manager import secret_manager

from ledger.app.ports.output.receipt_vision_parser_port import (
    ExtractedReceiptItem,
    ReceiptExtraction,
    ReceiptVisionParserPort,
)

_MODEL = "gemini-flash-latest"

_PROMPT = (
    "이 영수증 이미지를 분석해서 정보를 추출해줘. "
    "purchase_date는 반드시 YYYY-MM-DD 형식으로. "
    "category는 식비/교통/주거/생활/의료/문화/기타 중 가장 알맞은 하나로 분류해줘. "
    "품목(items)을 읽을 수 없으면 빈 배열로 둬도 돼."
)


class _ReceiptItemSchema(BaseModel):
    name: str
    quantity: float
    unit_price: float
    amount: float


class _ReceiptExtractionSchema(BaseModel):
    store_name: str
    purchase_date: str
    total_amount: float
    category: str
    items: list[_ReceiptItemSchema]


class GeminiReceiptVisionParserAdapter(ReceiptVisionParserPort):
    """Outbound 어댑터 — Gemini 멀티모달로 영수증 이미지를 직접 읽어 구조화한다 (별도 OCR 엔진 없음)."""

    def __init__(self, api_key: str | None = None, model: str = _MODEL) -> None:
        resolved_key = api_key or secret_manager.get_secret("GEMINI_API_KEY")
        self._client = genai.Client(api_key=resolved_key)
        self._model = model

    async def parse(self, data: bytes, content_type: str) -> ReceiptExtraction:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=[
                types.Part.from_bytes(data=data, mime_type=content_type),
                _PROMPT,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_ReceiptExtractionSchema,
            ),
        )
        parsed = response.parsed
        if not isinstance(parsed, _ReceiptExtractionSchema):
            raise ValueError("Gemini가 영수증 정보를 구조화된 형식으로 반환하지 않았습니다.")

        return ReceiptExtraction(
            store_name=parsed.store_name,
            purchase_date=_parse_date(parsed.purchase_date),
            total_amount=parsed.total_amount,
            category=parsed.category,
            items=[
                ExtractedReceiptItem(
                    name=item.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    amount=item.amount,
                )
                for item in parsed.items
            ],
        )


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()
