from dataclasses import dataclass, field

_DEFAULT_DEFECT_TYPES = ("crack", "scratch", "discoloration")


@dataclass(frozen=True)
class AnomalyDetectCommand:

    image: bytes
    defect_types: list[str] = field(default_factory=lambda: list(_DEFAULT_DEFECT_TYPES))
    threshold: float = 0.5


@dataclass(frozen=True)
class DefectScore:

    defect_type: str
    score: float


@dataclass(frozen=True)
class AnomalyDetectResult:

    is_anomaly: bool
    anomaly_score: float
    defect_category: str
    defect_scores: list[DefectScore]
