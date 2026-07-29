from functools import lru_cache

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.resource_adapters.sentiment_analysis.sentiment_classifier_model_adapter import (
    SentimentClassifierModelAdapter,
)
from ontology.app.ports.input.sentiment_analysis_use_case import SentimentAnalysisUseCase
from ontology.app.ports.output.sentiment_analysis_model_port import SentimentAnalysisModelPort
from ontology.app.use_cases.sentiment_analysis_interactor import SentimentAnalysisInteractor


@lru_cache(maxsize=1)
def get_sentiment_model_port() -> SentimentAnalysisModelPort:
    # 가중치 로드 비용이 커서 요청마다 새로 만들지 않고 캐싱한다.
    model_id = secret_manager.get_secret("SENTIMENT_ANALYSIS_MODEL_ID", "monologg/koelectra-base-finetuned-nsmc")
    device = secret_manager.get_secret("SENTIMENT_ANALYSIS_DEVICE", "cpu")
    return SentimentClassifierModelAdapter(model_id=model_id, device=device)


def get_sentiment_analysis_use_case() -> SentimentAnalysisUseCase:
    return SentimentAnalysisInteractor(model=get_sentiment_model_port())
