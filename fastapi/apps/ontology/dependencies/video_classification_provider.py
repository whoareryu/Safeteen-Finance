from functools import lru_cache

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.resource_adapters.video_classification.videomae_model_adapter import (
    VideoMaeModelAdapter,
)
from ontology.app.ports.input.video_classification_use_case import VideoClassificationUseCase
from ontology.app.ports.output.video_classification_model_port import VideoClassificationModelPort
from ontology.app.use_cases.video_classification_interactor import VideoClassificationInteractor


@lru_cache(maxsize=1)
def get_video_classification_model_port() -> VideoClassificationModelPort:
    # 가중치 로드 비용이 커서 요청마다 새로 만들지 않고 캐싱한다.
    model_id = secret_manager.get_secret("VIDEO_CLASSIFICATION_MODEL_ID", "MCG-NJU/videomae-base-finetuned-kinetics")
    device = secret_manager.get_secret("VIDEO_CLASSIFICATION_DEVICE", "cpu")
    return VideoMaeModelAdapter(model_id=model_id, device=device)


def get_video_classification_use_case() -> VideoClassificationUseCase:
    return VideoClassificationInteractor(model=get_video_classification_model_port())
