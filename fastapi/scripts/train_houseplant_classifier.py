"""하우스플랜트 품종 분류기 재학습 — 기존 plant_yolo.pt(농작물 병해용) 대체.

기존 apps/plant/resources/plant_yolo.pt는 PlantVillage(농작물) 클래스로만
학습돼 있어 몬스테라·스킨답서스 같은 반려식물 사진에는 근본적으로 대응하지
못한다(정답 클래스 자체가 없음). 이 스크립트는 동일한 베이스 모델·하이퍼
파라미터(체크포인트에서 복원: yolo11n-cls.pt, epochs=15, batch=32, imgsz=224)
로 하우스플랜트 품종 데이터셋을 새로 학습한다.

1차 범위는 "품종(species)"만 — 하우스플랜트용 증상/병충해 라벨 데이터셋은
공개적으로 확보되지 않아 이번 학습에는 포함하지 않는다. 증상 판단은 당분간
텍스트 생성 쪽(CareGuideInteractor)에서 처리한다.

사전 준비:
  pip install -r scripts/requirements-train.txt
  python scripts/download_houseplant_dataset.py --output <data-dir> 로 데이터 준비

사용 (Colab GPU 런타임 권장 — CPU도 가능하나 느림):
  python scripts/train_houseplant_classifier.py --data apps/plant/resources/yolo_train_houseplant

학습 후:
  1) runs/classify/train/weights/best.pt 를 apps/plant/resources/plant_yolo.pt로 교체
     (교체 전 기존 파일은 백업 권장: plant_yolo_crop_disease.pt 등)
  2) apps/plant/domain/value_objects/plant_label_translator.py 와
     www/lib/plant-labels.ts 의 SPECIES_KO에 새 품종 라벨(학습 로그에 출력되는
     클래스 목록) 한글 표기를 추가
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

_BASE_MODEL = "yolo11n-cls.pt"


def main() -> None:
    parser = argparse.ArgumentParser(description="하우스플랜트 품종 YOLO 분류기 학습")
    parser.add_argument("--data", required=True, help="download_houseplant_dataset.py 출력 디렉터리")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument(
        "--copy-to", default=None,
        help="학습 완료 후 best.pt를 이 경로로 복사(예: apps/plant/resources/plant_yolo_houseplant.pt). "
        "생략 시 복사하지 않고 runs/ 경로만 안내한다.",
    )
    args = parser.parse_args()

    model = YOLO(_BASE_MODEL)
    results = model.train(data=args.data, epochs=args.epochs, batch=args.batch, imgsz=args.imgsz)

    best_path = Path(results.save_dir) / "weights" / "best.pt"
    print(f"학습 완료: {best_path}")
    print(f"클래스 목록: {list(model.names.values())}")

    if args.copy_to:
        dest = Path(args.copy_to)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_path, dest)
        print(f"복사 완료: {dest}")
    else:
        print("--copy-to 를 지정하지 않아 복사는 생략했습니다. 위 경로에서 직접 옮겨주세요.")


if __name__ == "__main__":
    main()
