from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectDetectCommand:

    image: bytes
    score_threshold: float = 0.5


@dataclass(frozen=True)
class BoundingBox:

    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class DetectedObject:

    label: str
    confidence: float
    box: BoundingBox


@dataclass(frozen=True)
class ObjectDetectResult:

    objects: list[DetectedObject]
    instance_count: int
