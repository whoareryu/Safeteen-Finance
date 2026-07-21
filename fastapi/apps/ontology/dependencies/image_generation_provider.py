import os
from functools import lru_cache
from pathlib import Path

from ontology.adapter.outbound.filesystem.local_image_storage_adapter import (
    LocalImageStorageAdapter,
)
from ontology.adapter.outbound.resource_adapters.image_generation.sdxl_turbo_model_adapter import (
    SdxlTurboModelAdapter,
)
from ontology.app.ports.input.image_generation_use_case import ImageGenerationUseCase
from ontology.app.ports.output.image_generation_model_port import ImageGenerationModelPort
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway
from ontology.app.use_cases.image_generation_interactor import ImageGenerationInteractor

_DEFAULT_MEDIA_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / "resources" / "generated_images"


@lru_cache(maxsize=1)
def get_generation_model_port() -> ImageGenerationModelPort:
    # 가중치 로드 비용이 매우 커서(수 GB) 요청마다 새로 만들지 않고 캐싱한다.
    model_id = os.getenv("IMAGE_GENERATION_MODEL_ID", "stabilityai/sdxl-turbo")
    lora_weights_path = os.getenv("IMAGE_GENERATION_LORA_PATH") or None
    device = os.getenv("IMAGE_GENERATION_DEVICE", "cpu")
    return SdxlTurboModelAdapter(
        model_id=model_id, lora_weights_path=lora_weights_path, device=device
    )


def get_generation_storage_gateway() -> ImageStorageGateway:
    # VISION_S3_BUCKET용 AWS 자격증명이 아직 없어(.env AWS_ACCESS_KEY_ID 비어있음) 로컬 디스크로 대체.
    # 자격증명 발급 후 S3ImageStorageGateway로 교체.
    return LocalImageStorageAdapter(
        base_dir=_DEFAULT_MEDIA_DIR,
        public_base_url=os.getenv("BACKEND_PUBLIC_URL", "http://127.0.0.1:8000"),
        url_prefix="media/generated",
    )


def get_image_generation_use_case() -> ImageGenerationUseCase:
    return ImageGenerationInteractor(
        model=get_generation_model_port(), storage=get_generation_storage_gateway()
    )
