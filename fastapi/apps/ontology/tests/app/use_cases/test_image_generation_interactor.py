from __future__ import annotations

from ontology.app.dtos.image_generation_dto import ImageGenerateCommand
from ontology.app.ports.output.image_generation_model_port import ImageGenerationModelPort
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway
from ontology.app.use_cases.image_generation_interactor import ImageGenerationInteractor


class _FakeModelPort(ImageGenerationModelPort):
    def __init__(self, image_bytes: bytes, seed: int) -> None:
        self._image_bytes = image_bytes
        self._seed = seed
        self.received_command: ImageGenerateCommand | None = None

    def generate(self, command: ImageGenerateCommand) -> tuple[bytes, int]:
        self.received_command = command
        return self._image_bytes, self._seed

    def model_name(self) -> str:
        return "fake-sdxl-turbo"


class _FakeStorageGateway(ImageStorageGateway):
    def __init__(self, url: str) -> None:
        self._url = url
        self.received_content_type: str | None = None
        self.received_data: bytes | None = None

    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        self.received_content_type = content_type
        self.received_data = data
        return self._url


async def test_generate_orchestrates_model_and_storage() -> None:
    model = _FakeModelPort(image_bytes=b"fake-png-bytes", seed=42)
    storage = _FakeStorageGateway(url="http://example.com/media/generated/abc.png")
    interactor = ImageGenerationInteractor(model=model, storage=storage)
    command = ImageGenerateCommand(prompt="a cat", num_inference_steps=2, guidance_scale=0.0)

    result = await interactor.generate(command)

    assert result.image_url == "http://example.com/media/generated/abc.png"
    assert result.seed == 42
    assert result.steps == 2
    assert result.model == "fake-sdxl-turbo"
    assert model.received_command is command
    assert storage.received_content_type == "image/png"
    assert storage.received_data == b"fake-png-bytes"
