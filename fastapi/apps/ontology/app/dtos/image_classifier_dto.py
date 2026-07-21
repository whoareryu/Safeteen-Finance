from dataclasses import dataclass


@dataclass(frozen=True)
class ImageClassifyCommand:

    image: bytes
    backend: str = "convnext"  # "convnext" | "yolo"


@dataclass(frozen=True)
class ImageClassifyResult:

    label: str
    confidence: float
