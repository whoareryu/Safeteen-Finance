# Agent 02 — 물체 감지 (Object Detection)
> **원본 모델**: SSD (Single Shot Detector)  
> **대체 모델**: RT-DETR-L (Real-Time Detection Transformer) + QLoRA  
> **환경**: MacBook M5 · 24GB Unified Memory

---

## 1. 왜 SSD를 대체하는가?

| 항목 | SSD300 | RT-DETR-L (대체) |
|------|--------|------------------|
| 백본 | VGG16 | ResNet-50 + Transformer |
| mAP (COCO) | 41.2 | 53.0 |
| Anchor 설계 | 수동 설정 필요 | Anchor-Free (자동) |
| 소형 객체 감지 | 취약 | 강함 (Cross-Scale Attention) |
| QLoRA 파인튜닝 | 불가 | 가능 (Encoder 부분 학습) |
| 실시간 여부 | 46 FPS | 74 FPS (M5 MPS 기준) |

---

## 2. 추천 모델 상세

### 기본 추천: `PekingU/rtdetr_r50vd`
```
허깅페이스 ID : PekingU/rtdetr_r50vd
파라미터     : 42M
mAP (COCO)  : 53.0
입력 해상도  : 640×640 (가변 가능)
라이선스     : Apache 2.0
```

### 경량 대안: `hustvl/yolos-small`
```
허깅페이스 ID : hustvl/yolos-small
파라미터     : 30M
특징         : ViT 기반 YOLO → 분류 에이전트와 백본 공유 가능
mAP (COCO)  : 36.1 (속도 우선 시 선택)
```

---

## 3. QLoRA 파인튜닝 설정 (M5 24GB 최적화)

### 3-1. 환경 설치
```bash
pip install transformers datasets peft accelerate
pip install supervision  # 바운딩박스 시각화
```

### 3-2. RT-DETR QLoRA 설정
```python
from transformers import RTDetrForObjectDetection, RTDetrImageProcessor
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    # RT-DETR Transformer Encoder의 attention 레이어 대상
    target_modules=[
        "encoder.encoder.*.self_attn.q_proj",
        "encoder.encoder.*.self_attn.v_proj",
        "decoder.layers.*.self_attn.q_proj",
        "decoder.layers.*.self_attn.v_proj",
    ],
    lora_dropout=0.1,
    bias="none",
    task_type="OBJECT_DETECTION"
)

model = RTDetrForObjectDetection.from_pretrained(
    "PekingU/rtdetr_r50vd",
    torch_dtype=torch.float16,
    device_map="mps"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# 예상: trainable 약 1.2M / 42M (2.8%)
```

### 3-3. 학습 설정
```python
training_args = TrainingArguments(
    output_dir="./rtdetr-finetuned",
    per_device_train_batch_size=8,    # 640×640 이미지, M5 24GB 기준
    gradient_accumulation_steps=4,   # 유효 배치 32
    num_train_epochs=50,
    learning_rate=1e-4,
    fp16=True,
    warmup_steps=100,
    weight_decay=0.0001,
    save_strategy="epoch",
)
```

### 3-4. 커스텀 데이터셋 포맷 (COCO JSON)
```python
from datasets import load_dataset

# COCO 포맷 데이터셋 로드
dataset = load_dataset("json", data_files={
    "train": "annotations/train.json",
    "val": "annotations/val.json"
})
```

---

## 4. 멀티에이전트 역할 정의

```yaml
agent_id: detection_agent
role: "물체 감지 & 위치 추정"
input:
  - type: image
    format: [jpg, png]
    size: 640x640          # 자동 리사이즈
  - type: feature_vector   # classification_agent CLS 토큰 (선택)
    shape: [768]
output:
  - bounding_boxes: List[{x, y, w, h}]
  - class_labels: List[str]
  - confidence_scores: List[float]
  - instance_count: int
downstream_agents:
  - segmentation_agent    # ROI 영역 전달
  - pose_agent            # 인체 감지 시 전달
  - anomaly_agent         # 감지된 객체 이상 여부 확인
upstream_agents:
  - classification_agent  # 전체 이미지 사전 필터링
```

---

## 5. 최적화 툴 & 스킬

### 필수 툴
| 툴 | 용도 | 설치 |
|----|------|------|
| `supervision` | BBox 시각화·필터링 | `pip install supervision` |
| `albumentations` | 객체 감지 특화 증강 | `pip install albumentations` |
| `roboflow` | 데이터셋 관리·라벨링 | `pip install roboflow` |
| `fiftyone` | 데이터셋 시각화·분석 | `pip install fiftyone` |

### NMS 후처리 커스터마이징
```python
import torchvision.ops as ops

def apply_nms(predictions, iou_threshold=0.5, score_threshold=0.3):
    boxes = predictions["boxes"]
    scores = predictions["scores"]
    
    # 신뢰도 필터링
    mask = scores > score_threshold
    boxes, scores = boxes[mask], scores[mask]
    
    # NMS 적용
    keep_indices = ops.nms(boxes, scores, iou_threshold)
    return boxes[keep_indices], scores[keep_indices]
```

### 추천 스킬 체크리스트
- [ ] COCO 포맷 데이터 전처리 자동화
- [ ] Anchor-Free 원리 이해 (bipartite matching)
- [ ] mAP@0.5, mAP@0.5:0.95 평가 구현
- [ ] 클래스 불균형 처리 (focal loss 튜닝)
- [ ] TorchScript 변환으로 추론 최적화

---

## 6. 성능 벤치마크 예상치 (M5 24GB)

| 작업 | 예상 수치 |
|------|----------|
| 단일 이미지 추론 (640×640) | ~14ms |
| 실시간 처리 | ~71 FPS |
| QLoRA 학습 (1 epoch, 5k 이미지) | ~25분 |
| 모델 로드 시간 | ~4초 |

---

## 7. 에이전트 파이프라인 예시

```python
class DetectionAgent:
    def __init__(self):
        self.processor = RTDetrImageProcessor.from_pretrained("PekingU/rtdetr_r50vd")
        self.model = RTDetrForObjectDetection.from_pretrained(
            "./rtdetr-finetuned",   # LoRA 어댑터 포함
            torch_dtype=torch.float16
        ).to("mps")
    
    def detect(self, image: PIL.Image) -> dict:
        inputs = self.processor(images=image, return_tensors="pt").to("mps")
        with torch.no_grad():
            outputs = self.model(**inputs)
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=[image.size[::-1]], threshold=0.5
        )
        return results[0]   # boxes, scores, labels
```
