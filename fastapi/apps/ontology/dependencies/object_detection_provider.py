import os
from functools import lru_cache

from ontology.adapter.outbound.resource_adapters.object_detection.rtdetr_model_adapter import (
    RtDetrModelAdapter,
)
from ontology.app.ports.input.object_detection_use_case import ObjectDetectionUseCase
from ontology.app.ports.output.object_detection_model_port import ObjectDetectionModelPort
from ontology.app.use_cases.object_detection_interactor import ObjectDetectionInteractor


@lru_cache(maxsize=1)
def get_object_detection_model_port() -> ObjectDetectionModelPort:
    # 가중치 로드 비용이 커서 요청마다 새로 만들지 않고 캐싱한다.
    model_id = os.getenv("OBJECT_DETECTION_MODEL_ID", "PekingU/rtdetr_r50vd")
    device = os.getenv("OBJECT_DETECTION_DEVICE", "cpu")
    return RtDetrModelAdapter(model_id=model_id, device=device)


def get_object_detection_use_case() -> ObjectDetectionUseCase:
    return ObjectDetectionInteractor(model=get_object_detection_model_port())
