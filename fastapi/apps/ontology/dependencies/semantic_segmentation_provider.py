import os
from functools import lru_cache
from pathlib import Path

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.filesystem.local_image_storage_adapter import (
    LocalImageStorageAdapter,
)
from ontology.adapter.outbound.resource_adapters.semantic_segmentation.segformer_model_adapter import (
    SegformerModelAdapter,
)
from ontology.app.ports.input.semantic_segmentation_use_case import SemanticSegmentationUseCase
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway
from ontology.app.ports.output.semantic_segmentation_model_port import (
    SemanticSegmentationModelPort,
)
from ontology.app.use_cases.semantic_segmentation_interactor import SemanticSegmentationInteractor

_DEFAULT_MEDIA_DIR = (
    Path(os.path.dirname(os.path.dirname(__file__))) / "resources" / "segmentation_overlays"
)


@lru_cache(maxsize=1)
def get_segmentation_model_port() -> SemanticSegmentationModelPort:
    # 가중치 로드 비용이 커서 요청마다 새로 만들지 않고 캐싱한다.
    model_id = secret_manager.get_secret(
        "SEMANTIC_SEGMENTATION_MODEL_ID", "nvidia/segformer-b2-finetuned-ade-512-512"
    )
    device = secret_manager.get_secret("SEMANTIC_SEGMENTATION_DEVICE", "cpu")
    return SegformerModelAdapter(model_id=model_id, device=device)


def get_segmentation_storage_gateway() -> ImageStorageGateway:
    return LocalImageStorageAdapter(
        base_dir=_DEFAULT_MEDIA_DIR,
        public_base_url=secret_manager.get_secret("BACKEND_PUBLIC_URL", "http://127.0.0.1:8000"),
        url_prefix="media/segmentation",
    )


def get_semantic_segmentation_use_case() -> SemanticSegmentationUseCase:
    return SemanticSegmentationInteractor(
        model=get_segmentation_model_port(), storage=get_segmentation_storage_gateway()
    )
