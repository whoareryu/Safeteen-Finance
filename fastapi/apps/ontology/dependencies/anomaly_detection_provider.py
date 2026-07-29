from functools import lru_cache

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.resource_adapters.anomaly_detection.winclip_model_adapter import (
    WinClipModelAdapter,
)
from ontology.app.ports.input.anomaly_detection_use_case import AnomalyDetectionUseCase
from ontology.app.ports.output.anomaly_detection_model_port import AnomalyDetectionModelPort
from ontology.app.use_cases.anomaly_detection_interactor import AnomalyDetectionInteractor


@lru_cache(maxsize=1)
def get_anomaly_detection_model_port() -> AnomalyDetectionModelPort:
    # 가중치 로드 비용이 커서 요청마다 새로 만들지 않고 캐싱한다.
    model_id = secret_manager.get_secret("ANOMALY_DETECTION_MODEL_ID", "openai/clip-vit-base-patch32")
    device = secret_manager.get_secret("ANOMALY_DETECTION_DEVICE", "cpu")
    return WinClipModelAdapter(model_id=model_id, device=device)


def get_anomaly_detection_use_case() -> AnomalyDetectionUseCase:
    return AnomalyDetectionInteractor(model=get_anomaly_detection_model_port())
