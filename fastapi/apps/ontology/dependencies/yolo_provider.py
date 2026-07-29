import os

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.resource_adapters.yolo.yolo_dataset_adapter import YoloDatasetAdapter
from ontology.adapter.outbound.resource_adapters.yolo.yolo_model_adapter import YoloModelAdapter
from ontology.app.ports.input.yolo_use_case import YoloUseCase
from ontology.app.ports.output.yolo_model_port import YoloModelPort
from ontology.app.ports.output.yolo_port import YoloPort
from ontology.app.use_cases.yolo_interactor import YoloInteractor

_DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "resources", "yolo_train"
)
_DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "resources", "models", "yolo_face_classifier.pt"
)


def get_yolo_port() -> YoloPort:
    base_path = secret_manager.get_secret("YOLO_DATASET_PATH", _DEFAULT_DATASET_PATH)
    return YoloDatasetAdapter(base_path=base_path)


def get_yolo_model_port() -> YoloModelPort:
    model_path = secret_manager.get_secret("YOLO_MODEL_PATH", _DEFAULT_MODEL_PATH)
    return YoloModelAdapter(model_path=model_path)


def get_yolo_use_case() -> YoloUseCase:
    return YoloInteractor(dataset=get_yolo_port(), model=get_yolo_model_port())
