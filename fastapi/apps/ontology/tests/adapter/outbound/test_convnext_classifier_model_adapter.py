from __future__ import annotations

import io
import json

import pytest
import timm
import torch
from PIL import Image

from ontology.adapter.outbound.resource_adapters.image_classifier.convnext_classifier_model_adapter import (
    ConvNeXtClassifierModelAdapter,
    _preprocess_bytes,
)

_NUM_CLASSES = 3
_CLASS_NAMES = ["장미", "튤립", "해바라기"]


def _make_image_bytes(fmt: str, mode: str = "RGB", size: tuple[int, int] = (300, 300)) -> bytes:
    image = Image.new(mode, size, color="green")
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def _sample_jpeg_bytes() -> bytes:
    return _make_image_bytes("JPEG")


# ---------------------------------------------------------------------------
# _preprocess_bytes (순수 함수)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("fmt", ["JPEG", "PNG"])
def test_preprocess_bytes_returns_expected_shape(fmt: str) -> None:
    tensor = _preprocess_bytes(_make_image_bytes(fmt))
    assert tensor.shape == (1, 3, 224, 224)


def test_preprocess_bytes_converts_rgba_to_rgb() -> None:
    tensor = _preprocess_bytes(_make_image_bytes("PNG", mode="RGBA"))
    assert tensor.shape == (1, 3, 224, 224)


def test_preprocess_bytes_rejects_unsupported_format() -> None:
    with pytest.raises(ValueError):
        _preprocess_bytes(_make_image_bytes("BMP"))


def test_preprocess_bytes_rejects_non_image_data() -> None:
    with pytest.raises(ValueError):
        _preprocess_bytes(b"not an image")


# ---------------------------------------------------------------------------
# ConvNeXtClassifierModelAdapter
# ---------------------------------------------------------------------------
@pytest.fixture()
def adapter(tmp_path) -> ConvNeXtClassifierModelAdapter:
    """실제 파인튜닝 가중치 없이, 랜덤 초기화된 convnext_nano를 임시 파일로 저장해 로드한다."""
    model = timm.create_model("convnext_nano", pretrained=False, num_classes=_NUM_CLASSES)
    weights_path = tmp_path / "random_weights.pth"
    torch.save(model.state_dict(), weights_path)

    class_names_path = tmp_path / "class_names.json"
    class_names_path.write_text(json.dumps(_CLASS_NAMES, ensure_ascii=False), encoding="utf-8")

    return ConvNeXtClassifierModelAdapter(
        weights_path=str(weights_path), class_names_path=str(class_names_path), device="cpu"
    )


def test_predict_returns_label_from_class_names_and_confidence_between_0_and_1(
    adapter: ConvNeXtClassifierModelAdapter,
) -> None:
    result = adapter.predict(_sample_jpeg_bytes())
    assert result.label in _CLASS_NAMES
    assert 0.0 <= result.confidence <= 1.0


def test_predict_rejects_non_image_bytes(adapter: ConvNeXtClassifierModelAdapter) -> None:
    with pytest.raises(ValueError):
        adapter.predict(b"not an image")


def test_missing_weights_file_raises_runtime_error(tmp_path) -> None:
    class_names_path = tmp_path / "class_names.json"
    class_names_path.write_text(json.dumps(_CLASS_NAMES), encoding="utf-8")
    with pytest.raises(RuntimeError):
        ConvNeXtClassifierModelAdapter(
            weights_path=str(tmp_path / "missing.pth"),
            class_names_path=str(class_names_path),
            device="cpu",
        )
