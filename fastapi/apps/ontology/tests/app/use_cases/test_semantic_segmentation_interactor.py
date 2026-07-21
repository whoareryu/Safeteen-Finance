from __future__ import annotations

from ontology.app.dtos.semantic_segmentation_dto import (
    ClassArea,
    SegmentCommand,
    SegmentModelOutput,
)
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway
from ontology.app.ports.output.semantic_segmentation_model_port import (
    SemanticSegmentationModelPort,
)
from ontology.app.use_cases.semantic_segmentation_interactor import SemanticSegmentationInteractor


class _FakeModelPort(SemanticSegmentationModelPort):
    def __init__(self, output: SegmentModelOutput) -> None:
        self._output = output
        self.received_bytes: bytes | None = None

    def segment(self, image_bytes: bytes) -> SegmentModelOutput:
        self.received_bytes = image_bytes
        return self._output


class _FakeStorageGateway(ImageStorageGateway):
    def __init__(self, url: str) -> None:
        self._url = url
        self.received_content_type: str | None = None
        self.received_data: bytes | None = None

    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        self.received_content_type = content_type
        self.received_data = data
        return self._url


async def test_segment_orchestrates_model_and_storage() -> None:
    output = SegmentModelOutput(
        class_areas=[ClassArea(label="wall", ratio=0.6), ClassArea(label="sky", ratio=0.4)],
        overlay_png=b"fake-png-bytes",
    )
    model = _FakeModelPort(output)
    storage = _FakeStorageGateway(url="http://example.com/media/segmentation/abc.png")
    interactor = SemanticSegmentationInteractor(model=model, storage=storage)

    result = await interactor.segment(SegmentCommand(image=b"fake-image-bytes"))

    assert result.overlay_image_url == "http://example.com/media/segmentation/abc.png"
    assert result.class_areas == output.class_areas
    assert model.received_bytes == b"fake-image-bytes"
    assert storage.received_content_type == "image/png"
    assert storage.received_data == b"fake-png-bytes"
