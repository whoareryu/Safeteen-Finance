from dataclasses import dataclass


@dataclass(frozen=True)
class VideoClassifyCommand:

    video: bytes
    filename: str


@dataclass(frozen=True)
class LabelScore:

    label: str
    score: float


@dataclass(frozen=True)
class ClipSegment:

    start_sec: float
    end_sec: float
    label: str
    confidence: float


@dataclass(frozen=True)
class VideoClassifyResult:

    action_label: str
    confidence: float
    top_k_labels: list[LabelScore]
    clip_segments: list[ClipSegment]
