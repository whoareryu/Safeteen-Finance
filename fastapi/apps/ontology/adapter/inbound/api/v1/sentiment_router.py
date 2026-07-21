import asyncio

from fastapi import APIRouter, Depends, HTTPException

from ontology.adapter.inbound.api.schemas.sentiment_analysis_schema import (
    SentimentAnalyzeRequest,
    SentimentAnalyzeResponse,
)
from ontology.app.dtos.sentiment_analysis_dto import SentimentAnalyzeCommand
from ontology.app.ports.input.sentiment_analysis_use_case import SentimentAnalysisUseCase
from ontology.dependencies.sentiment_analysis_provider import get_sentiment_analysis_use_case

sentiment_router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@sentiment_router.post(
    "/analyze",
    response_model=SentimentAnalyzeResponse,
    responses={400: {"description": "빈 텍스트"}},
    summary="한국어 텍스트 감정 분석 (NSMC 파인튜닝 KoELECTRA 기본, 모델 교체 가능)",
)
async def analyze_sentiment(
    body: SentimentAnalyzeRequest,
    use_case: SentimentAnalysisUseCase = Depends(get_sentiment_analysis_use_case),
) -> SentimentAnalyzeResponse:
    try:
        result = await asyncio.to_thread(
            use_case.analyze, SentimentAnalyzeCommand(text=body.text)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return SentimentAnalyzeResponse(
        sentiment=result.sentiment,
        confidence=result.confidence,
        scores=[{"label": s.label, "score": s.score} for s in result.scores],
    )
