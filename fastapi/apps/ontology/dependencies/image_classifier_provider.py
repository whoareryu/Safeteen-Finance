import os
from functools import lru_cache

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.resource_adapters.image_classifier.convnext_classifier_model_adapter import (
    ConvNeXtClassifierModelAdapter,
)
from ontology.adapter.outbound.resource_adapters.image_classifier.yolo_classifier_model_adapter import (
    YoloClassifierModelAdapter,
)
from ontology.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from ontology.app.use_cases.image_classifier_interactor import ImageClassifierInteractor
from ontology.dependencies.yolo_provider import get_yolo_model_port

_DEFAULT_WEIGHTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "resources", "models", "convnext_nano_ft.pth"
)
_DEFAULT_CLASS_NAMES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "resources", "models", "image_classifier_class_names.json",
)


@lru_cache(maxsize=1)
def get_convnext_backend() -> ImageClassifierModelPort:
    # 가중치 로드 비용이 커서 요청마다 새로 만들지 않고 캐싱한다. 실제로 요청될 때만
    # (backend=convnext) 호출되므로, 가중치가 없어도 다른 backend는 영향받지 않는다.
    weights_path = secret_manager.get_secret("IMAGE_CLASSIFIER_WEIGHTS_PATH", _DEFAULT_WEIGHTS_PATH)
    class_names_path = secret_manager.get_secret(
        "IMAGE_CLASSIFIER_CLASS_NAMES_PATH", _DEFAULT_CLASS_NAMES_PATH
    )
    device = secret_manager.get_secret("IMAGE_CLASSIFIER_DEVICE", "cpu")
    return ConvNeXtClassifierModelAdapter(
        weights_path=weights_path, class_names_path=class_names_path, device=device
    )


@lru_cache(maxsize=1)
def get_yolo_backend() -> ImageClassifierModelPort:
    return YoloClassifierModelAdapter(model_port=get_yolo_model_port())


def get_image_classifier_use_case() -> ImageClassifierUseCase:
    return ImageClassifierInteractor(
        backend_factories={
            "convnext": get_convnext_backend,
            "yolo": get_yolo_backend,
        }
    )
