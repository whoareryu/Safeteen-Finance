from dataclasses import dataclass, field


@dataclass(frozen=True)
class YoloTrainCommand:

    epochs: int = 50
    batch_size: int = 16
    imgsz: int = 224
    device: str = "mps"


@dataclass(frozen=True)
class YoloTrainResult:

    dataset_root: str
    epochs: int
    classes: list[str] = field(default_factory=list)
    weights_path: str = ""
