# Agent 08 — 동영상 분류 (Video Classification)
> **원본 모델**: 3D CNN (C3D, I3D, SlowFast 등)  
> **대체 모델**: Video-MAE V2 (ViT 기반 Video Transformer) + QLoRA  
> **환경**: MacBook M5 · 24GB Unified Memory

---

## 1. 왜 3D CNN을 대체하는가?

| 항목 | C3D / I3D (3DCNN) | Video-MAE V2 (대체) |
|------|-------------------|---------------------|
| 아키텍처 | 3D Convolution | ViT + Tube Masking |
| Top-1 (Kinetics-400) | 79.9% (I3D) | 86.6% |
| 파라미터 수 | 28M (C3D) / 25M (I3D) | 86M (Base) |
| 시간 정보 처리 | 슬라이딩 윈도우 | 시공간 어텐션 (전역) |
| 긴 동영상 처리 | 취약 (고정 클립) | 상대적으로 강함 |
| QLoRA 적용 | 불가 (Conv 구조) | 가능 (Transformer 블록) |
| M5 MPS 지원 | 제한적 | 완전 지원 |
| 메모리 효율 | 낮음 (3D Conv 연산) | 높음 (Tube Masking) |

---

## 2. 추천 모델 상세

### 기본 추천: `MCG-NJU/videomae-base-finetuned-kinetics`
```
허깅페이스 ID : MCG-NJU/videomae-base-finetuned-kinetics
파라미터     : 86M
Top-1 (K400) : 81.5%
입력         : 16 프레임 × 224×224
사전학습     : Kinetics-400 (400개 액션 클래스)
라이선스     : CC BY-NC 4.0
```

### 고성능 추천: `MCG-NJU/videomae-large-finetuned-kinetics`
```
허깅페이스 ID : MCG-NJU/videomae-large-finetuned-kinetics
파라미터     : 307M
Top-1 (K400) : 85.8%
메모리 사용  : ~12GB fp16
특징         : 정확도 우선 시 선택, M5 24GB에서 단독 로드 가능
```

### 경량 대안: `facebook/timesformer-base-finetuned-k400`
```
허깅페이스 ID : facebook/timesformer-base-finetuned-k400
파라미터     : 121M
Top-1 (K400) : 78.0%
특징         : 공간/시간 어텐션 분리 → 메모리 효율↑, 추론 빠름
입력         : 8 프레임 × 224×224
라이선스     : Apache 2.0
```

### 실시간 경량 대안: `facebook/mvit-v2-small`
```
파라미터    : 34M
Top-1 (K400): 81.0%
특징        : Multiscale ViT, 3DCNN 수준 속도로 Transformer 성능
메모리      : ~3.5GB fp16
```

---

## 3. QLoRA 파인튜닝 설정 (M5 24GB 최적화)

### 3-1. 환경 설치
```bash
pip install transformers datasets peft accelerate
pip install decord          # 빠른 동영상 디코딩 (M5 권장)
pip install av              # PyAV (decord 대안)
pip install opencv-python   # 프레임 처리
pip install pytorchvideo    # Facebook 동영상 유틸리티
```

### 3-2. VideoMAE QLoRA 설정
```python
from transformers import VideoMAEForVideoClassification, VideoMAEImageProcessor
from peft import LoraConfig, get_peft_model, TaskType
import torch

# 분류 레이블 정의 (커스텀 태스크 예시)
VIDEO_LABELS = {
    0: "걷기",
    1: "달리기",
    2: "넘어짐",
    3: "앉기",
    4: "일어서기"
}

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    # VideoMAE ViT 블록의 시공간 어텐션 레이어
    target_modules=["query", "value"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.SEQ_CLS
)

processor = VideoMAEImageProcessor.from_pretrained(
    "MCG-NJU/videomae-base-finetuned-kinetics"
)

model = VideoMAEForVideoClassification.from_pretrained(
    "MCG-NJU/videomae-base-finetuned-kinetics",
    num_labels=len(VIDEO_LABELS),
    ignore_mismatched_sizes=True,   # 헤드 재초기화
    torch_dtype=torch.float16,
    device_map="mps"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# 예상: trainable 약 589K / 86M (0.68%)
```

### 3-3. 동영상 프레임 샘플링
```python
import decord
import numpy as np
from decord import VideoReader, cpu

def sample_frames(video_path: str, num_frames: int = 16) -> np.ndarray:
    """
    동영상에서 균등 간격으로 프레임 샘플링
    VideoMAE 기본 입력: 16 프레임
    """
    vr = VideoReader(video_path, ctx=cpu(0))
    total_frames = len(vr)

    # 균등 간격 인덱스 계산
    indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    frames = vr.get_batch(indices).asnumpy()   # [T, H, W, C]

    return frames   # uint8, RGB

def preprocess_video(video_path: str, processor) -> dict:
    """VideoMAE 입력 전처리"""
    frames = sample_frames(video_path, num_frames=16)
    # list of PIL or numpy arrays
    inputs = processor(list(frames), return_tensors="pt")
    return inputs   # pixel_values: [1, 16, 3, 224, 224]
```

### 3-4. 커스텀 데이터셋 클래스
```python
import torch
from torch.utils.data import Dataset
from pathlib import Path

class VideoDataset(Dataset):
    """
    폴더 구조:
    dataset/
      train/
        class_A/  video1.mp4  video2.mp4 ...
        class_B/  ...
      val/
        class_A/  ...
    """
    def __init__(self, root_dir: str, processor, num_frames: int = 16):
        self.root = Path(root_dir)
        self.processor = processor
        self.num_frames = num_frames

        self.samples = []
        self.label2id = {}

        for idx, class_dir in enumerate(sorted(self.root.iterdir())):
            if class_dir.is_dir():
                self.label2id[class_dir.name] = idx
                for video_file in class_dir.glob("*.mp4"):
                    self.samples.append((video_file, idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        video_path, label = self.samples[idx]
        frames = sample_frames(str(video_path), self.num_frames)
        inputs = self.processor(list(frames), return_tensors="pt")
        return {
            "pixel_values": inputs["pixel_values"].squeeze(0),  # [16, 3, 224, 224]
            "labels": torch.tensor(label, dtype=torch.long)
        }
```

### 3-5. 학습 설정 (M5 24GB 기준)
```python
from transformers import TrainingArguments, Trainer
import evaluate

training_args = TrainingArguments(
    output_dir="./videomae-finetuned",
    per_device_train_batch_size=2,    # 동영상은 메모리 집약적
    gradient_accumulation_steps=8,   # 유효 배치 = 16
    num_train_epochs=20,
    learning_rate=5e-5,
    fp16=True,
    warmup_ratio=0.1,
    weight_decay=0.05,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    dataloader_num_workers=2,         # 동영상 디코딩 병렬화
    remove_unused_columns=False,      # pixel_values 유지
)

accuracy_metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return accuracy_metric.compute(predictions=predictions, references=labels)

train_dataset = VideoDataset("./dataset/train", processor)
val_dataset   = VideoDataset("./dataset/val",   processor)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)
trainer.train()
```

---

## 4. 멀티에이전트 역할 정의

```yaml
agent_id: video_agent
role: "동영상 분류 & 시간적 행동 인식"
input:
  - type: video
    format: [mp4, avi, mov]
    fps: any                  # 내부적으로 16프레임 샘플링
    duration: 2~30초 권장
  - type: frame_sequence      # 이미 추출된 프레임 배열 (선택)
    shape: [T, H, W, C]
output:
  - action_label: str         # "걷기", "넘어짐" 등
  - confidence: float
  - top_k_labels: List[{label, score}]   # 상위 K개
  - temporal_features: tensor[768]       # 시간 특징 벡터
  - clip_segments: List[{start, end, label}]   # 구간별 분류
downstream_agents:
  - nlp_agent        # 행동 설명 자연어 생성 ("3초 구간에서 낙상 감지")
  - anomaly_agent    # 비정상 행동 패턴 플래깅
upstream_agents:
  - pose_agent       # 프레임별 스켈레톤 시퀀스 → 행동 인식 보조
  - detection_agent  # 영상 내 객체 감지 → 컨텍스트 제공
```

---

## 5. 고급 활용: 슬라이딩 윈도우 긴 영상 처리

```python
def classify_long_video(
    video_path: str,
    model,
    processor,
    clip_len: int = 16,
    stride: int = 8,          # 클립 간 겹침 (50%)
    threshold: float = 0.5
) -> list:
    """
    긴 영상을 슬라이딩 윈도우로 분할 분류
    stride < clip_len 이면 겹쳐서 매끄러운 결과
    """
    vr = VideoReader(video_path, ctx=cpu(0))
    total = len(vr)
    fps = vr.get_avg_fps()
    results = []

    for start in range(0, total - clip_len, stride):
        end = start + clip_len
        indices = np.linspace(start, end - 1, clip_len, dtype=int)
        frames = vr.get_batch(indices).asnumpy()

        inputs = processor(list(frames), return_tensors="pt").to("mps")
        with torch.no_grad():
            outputs = model(**inputs)

        probs = torch.softmax(outputs.logits, dim=-1)[0]
        top_label = VIDEO_LABELS[probs.argmax().item()]
        top_conf  = float(probs.max())

        if top_conf >= threshold:
            results.append({
                "start_sec": round(start / fps, 2),
                "end_sec":   round(end   / fps, 2),
                "label":     top_label,
                "confidence": top_conf
            })

    return results
```

---

## 6. TimeSformer 대안 사용 시 비교

```python
# TimeSformer: 공간-시간 어텐션 분리 → 더 빠름
from transformers import TimesformerForVideoClassification, AutoImageProcessor

timesformer_processor = AutoImageProcessor.from_pretrained(
    "facebook/timesformer-base-finetuned-k400"
)
timesformer_model = TimesformerForVideoClassification.from_pretrained(
    "facebook/timesformer-base-finetuned-k400",
    torch_dtype=torch.float16
).to("mps")

# 입력: 8 프레임 (VideoMAE의 절반 → 속도 2× 빠름)
frames_8 = sample_frames(video_path, num_frames=8)
inputs = timesformer_processor(list(frames_8), return_tensors="pt").to("mps")
```

---

## 7. 최적화 툴 & 스킬

### 필수 툴
| 툴 | 용도 | 설치 |
|----|------|------|
| `decord` | GPU/CPU 고속 동영상 디코딩 | `pip install decord` |
| `pytorchvideo` | 동영상 데이터 증강·유틸 | `pip install pytorchvideo` |
| `ffmpeg-python` | 동영상 전처리·변환 | `pip install ffmpeg-python` |
| `av` | 프레임 단위 정밀 제어 | `pip install av` |
| `supervision` | 동영상 위에 결과 오버레이 | `pip install supervision` |

### 데이터 증강 (동영상 특화)
```python
from pytorchvideo.transforms import (
    ApplyTransformToKey,
    RandomShortSideScale,
    UniformTemporalSubsample,
)
from torchvision.transforms import (
    Compose, RandomCrop, RandomHorizontalFlip, ColorJitter
)

video_transform = Compose([
    UniformTemporalSubsample(16),      # 균등 16프레임 샘플링
    RandomShortSideScale(min_size=256, max_size=320),
    RandomCrop(224),
    RandomHorizontalFlip(p=0.5),
    ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4),
])
```

### FFmpeg 전처리 (M5 하드웨어 가속)
```bash
# M5 VideoToolbox 하드웨어 가속 디코딩
ffmpeg -hwaccel videotoolbox \
       -i input.mp4 \
       -vf "scale=224:224,fps=30" \
       -c:v h264_videotoolbox \
       output_224.mp4

# 동영상 → 프레임 이미지 일괄 추출
ffmpeg -i input.mp4 -vf "fps=1" frames/frame_%04d.jpg
```

### 추천 스킬 체크리스트
- [ ] 균등 샘플링 vs. 밀집 샘플링 비교 (행동 특성에 따라 선택)
- [ ] Tube Masking 원리 이해 (VideoMAE 사전학습 핵심)
- [ ] 클립 길이 튜닝 (짧은 동작 8f, 긴 동작 32f)
- [ ] 시간 데이터 증강 (역재생, 속도 변환)
- [ ] `model.merge_and_unload()` 로 추론 최적화
- [ ] ONNX 변환 후 CoreML로 M5 엣지 배포
- [ ] 슬라이딩 윈도우 stride 튜닝 (겹침 비율 조절)
- [ ] pose_agent 스켈레톤 시퀀스와 late fusion 결합

---

## 8. 성능 벤치마크 예상치 (M5 24GB)

| 작업 | VideoMAE-Base | TimeSformer-Base | MViT-v2-Small |
|------|--------------|-----------------|---------------|
| 클립 추론 (16f) | ~45ms | ~25ms | ~20ms |
| 처리 가능 FPS | ~22 FPS | ~40 FPS | ~50 FPS |
| QLoRA 학습 (1 epoch, 1k 클립) | ~35분 | ~20분 | ~15분 |
| 모델 로드 | ~5초 | ~6초 | ~3초 |
| 메모리 사용 (fp16) | ~4GB | ~5GB | ~3.5GB |
| Top-1 (K400) | 81.5% | 78.0% | 81.0% |

> **M5 24GB 권장 선택**: 정확도 우선 → `VideoMAE-Base`, 실시간 처리 우선 → `MViT-v2-Small`

---

## 9. 멀티에이전트 통합 위치 (전체 파이프라인)

```
동영상 입력
    │
    ├──► video_agent (08)  ──────────────────────────────┐
    │    └─ 행동 레이블, 구간 분류                          │
    │                                                     │
    ├──► detection_agent (02) ─► pose_agent (04)         │
    │    └─ 프레임별 객체 감지      └─ 스켈레톤 시퀀스        │
    │                                   │ late fusion      │
    │                                   ▼                 │
    │                          video_agent 보조 입력       │
    │                                                     ▼
    └──────────────────────────────► nlp_agent (07)
                                     └─ "2.3초~4.1초 구간에서
                                         보행 중 낙상이 감지되었습니다"
```

---

## 10. 공개 동영상 데이터셋 (파인튜닝용)

```
Kinetics-400/600/700  : 범용 행동 인식 (400~700 클래스)
UCF-101               : 101개 스포츠/일상 행동
HMDB-51               : 51개 행동 (작은 규모, 빠른 실험)
AVA                   : 시공간 행동 위치화
FallDetection Dataset : 낙상 감지 특화 (살핌/PawLog 연계 가능)
AIHub 이상행동 CCTV   : 한국 공공 CCTV 이상행동 데이터
```
