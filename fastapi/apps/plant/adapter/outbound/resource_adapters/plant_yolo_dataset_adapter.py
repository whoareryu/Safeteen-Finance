from __future__ import annotations

import os

from ontology.app.ports.output.yolo_port import YoloPort


class PlantYoloDatasetAdapter(YoloPort):
    """로컬 디렉토리(train/<species>__<symptom>/*.jpg, val/...)에서 식물 진단 데이터셋을 제공한다."""

    def __init__(self, base_path: str) -> None:
        self._base_path = base_path

    def get_dataset_root(self) -> str:
        train_dir = os.path.join(self._base_path, "train")
        val_dir = os.path.join(self._base_path, "val")
        if not os.path.isdir(train_dir) or not os.path.isdir(val_dir):
            raise FileNotFoundError(
                f"식물 진단 데이터셋을 찾을 수 없습니다: {train_dir}, {val_dir} 에 "
                "품종__증상별 하위 폴더(예: train/monstera__overwatered_yellowing/*.jpg)를 채워주세요."
            )
        return self._base_path
