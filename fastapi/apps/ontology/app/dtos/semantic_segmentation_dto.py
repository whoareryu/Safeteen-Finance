from dataclasses import dataclass


@dataclass(frozen=True)
class SegmentCommand:

    image: bytes


@dataclass(frozen=True)
class ClassArea:

    label: str
    ratio: float


@dataclass(frozen=True)
class SegmentModelOutput:
    """모델 어댑터가 반환하는 원시 결과 — 오버레이는 저장 전 PNG bytes."""

    class_areas: list[ClassArea]
    overlay_png: bytes


@dataclass(frozen=True)
class SegmentResult:

    class_areas: list[ClassArea]
    overlay_image_url: str
