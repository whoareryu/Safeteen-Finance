from __future__ import annotations

import os

from ultralytics import YOLO

from ontology.app.dtos.yolo_dto import YoloTrainCommand, YoloTrainResult
from ontology.app.ports.input.yolo_use_case import YoloUseCase
from ontology.app.ports.output.yolo_model_port import YoloModelPort
from ontology.app.ports.output.yolo_port import YoloPort

_BASE_MODEL = "yolo11n-cls.pt"


class YoloInteractor(YoloUseCase):

    def __init__(self, dataset: YoloPort, model: YoloModelPort) -> None:
        self._dataset = dataset
        self._model = model

    def execute(self, command: YoloTrainCommand) -> YoloTrainResult:
        dataset_root = self._dataset.get_dataset_root()
        classes = sorted(os.listdir(os.path.join(dataset_root, "train")))

        model = YOLO(_BASE_MODEL)
        model.train(
            data=dataset_root,
            epochs=command.epochs,
            batch=command.batch_size,
            imgsz=command.imgsz,
            device=command.device,
        )
        weights_path = self._model.save(str(model.trainer.best))
        return YoloTrainResult(
            dataset_root=dataset_root,
            epochs=command.epochs,
            classes=classes,
            weights_path=weights_path,
        )
