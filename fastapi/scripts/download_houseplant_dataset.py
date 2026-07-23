"""반려식물(하우스플랜트) 품종 분류용 데이터셋 다운로드 + train/val 분할.

Kaggle "House Plant Species" 데이터셋(kacpergregorowicz/house-plant-species,
47종 약 14,790장, 클래스별 폴더 1개, train/val 분할 없음)을 내려받아
ultralytics YOLO classify가 요구하는 형식(output/train/{class}/*.jpg,
output/val/{class}/*.jpg)으로 재배치한다.

사전 준비:
  pip install -r scripts/requirements-train.txt
  Kaggle API 인증 필요 — 아래 둘 중 하나:
    1) ~/.kaggle/kaggle.json 배치 (Kaggle 계정 설정에서 발급)
    2) 환경변수 KAGGLE_USERNAME, KAGGLE_KEY 설정

사용 (Colab 등에서):
  python scripts/download_houseplant_dataset.py \
      --output apps/plant/resources/yolo_train_houseplant --val-ratio 0.15
"""

from __future__ import annotations

import argparse
import random
import re
import shutil
import tempfile
from pathlib import Path

_KAGGLE_DATASET = "kacpergregorowicz/house-plant-species"


def _slugify(name: str) -> str:
    """"Monstera Deliciosa" -> "monstera_deliciosa" (기존 라벨 컨벤션과 통일)."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower())
    return slug.strip("_")


def _download_raw(dest: Path) -> Path:
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    dest.mkdir(parents=True, exist_ok=True)
    api.dataset_download_files(_KAGGLE_DATASET, path=str(dest), unzip=True, quiet=False)
    return dest


def _split_into_train_val(raw_dir: Path, output_dir: Path, val_ratio: float, seed: int) -> None:
    class_dirs = [p for p in raw_dir.rglob("*") if p.is_dir() and any(p.iterdir())]
    # 가장 안쪽(리프) 클래스 폴더만 남긴다 — 데이터셋 압축 해제 시 생기는 중간 폴더 배제.
    class_dirs = [p for p in class_dirs if not any(c.is_dir() for c in p.iterdir())]

    rng = random.Random(seed)
    train_dir, val_dir = output_dir / "train", output_dir / "val"
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    for class_dir in class_dirs:
        images = [
            f for f in class_dir.iterdir()
            if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        ]
        if not images:
            continue
        rng.shuffle(images)
        cut = max(1, int(len(images) * (1 - val_ratio)))
        slug = _slugify(class_dir.name)

        for split_dir, files in ((train_dir, images[:cut]), (val_dir, images[cut:])):
            target = split_dir / slug
            target.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.copy2(f, target / f.name)

        print(f"{class_dir.name} -> {slug}: train={cut} val={len(images) - cut}")


def main() -> None:
    parser = argparse.ArgumentParser(description="하우스플랜트 품종 데이터셋 다운로드 + 분할")
    parser.add_argument(
        "--output", default="apps/plant/resources/yolo_train_houseplant",
        help="train/val을 생성할 출력 디렉터리",
    )
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output_dir = Path(args.output)
    with tempfile.TemporaryDirectory() as tmp:
        raw_dir = _download_raw(Path(tmp) / "raw")
        _split_into_train_val(raw_dir, output_dir, args.val_ratio, args.seed)

    print(f"완료: {output_dir}/train, {output_dir}/val")


if __name__ == "__main__":
    main()
