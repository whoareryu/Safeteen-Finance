from __future__ import annotations

from typing import Callable

from ontology.app.dtos.image_classifier_dto import ImageClassifyCommand, ImageClassifyResult
from ontology.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort


class ImageClassifierInteractor(ImageClassifierUseCase):
    """ontology 허브의 통합 이미지 분류 캐퍼빌리티 — backend별로 교체 가능한 어댑터를 지연 생성한다."""

    def __init__(self, backend_factories: dict[str, Callable[[], ImageClassifierModelPort]]) -> None:
        self._backend_factories = backend_factories

    def predict(self, command: ImageClassifyCommand) -> ImageClassifyResult:
        factory = self._backend_factories.get(command.backend)
        if factory is None:
            supported = ", ".join(sorted(self._backend_factories))
            raise ValueError(f"지원하지 않는 backend입니다: {command.backend} (지원: {supported})")
        model = factory()
        return model.predict(command.image)
