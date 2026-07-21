# Agent 03 — 시멘틱 분할 (Semantic Segmentation)
> **원본 모델**: PSPNet (Pyramid Scene Parsing Network)  
> **대체 모델**: SegFormer-B2 + QLoRA  
> **환경**: MacBook M5 · 24GB Unified Memory

---

## 1. 왜 PSPNet을 대체하는가?

| 항목 | PSPNet | SegFormer-B2 (대체) |
|------|--------|---------------------|
| 백본 | ResNet-101 | Mix Transformer (MiT-B2) |
| mIoU (ADE20K) | 43.3 | 51.1 |
| 파라미터 수 | 65M | 27M |
| Pyramid Pooling | 수동 스케일 설정 | 계층적 어텐션 (자동) |
| M5 메모리 사용 | 높음 (dilated conv) | 낮음 (효율적 어텐션) |
| QLoRA 적용 | 불가 | 가능 |

---

## 2. 추천 모델 상세

### 기본 추천: `nvidia/segformer-b2-finetuned-ade-512-512`
```
허깅페이스 ID : nvidia/segformer-b2-finetuned-ade-512-512
파라미터     : 27M
mIoU (ADE20K): 51.1
입력 해상도  : 512×512
지원 클래스  : 150개 (ADE20K 기준)
라이선스     : Apache 2.0
```

### 경량 대안: `nvidia/segformer-b0-finetuned-ade-512-512`
```
허깅페이스 ID : nvidia/segformer-b0-finetuned-ade-512-512
파라미터     : 3.7M
특징         : M5에서 실시간 처리 가능, 배터리 효율 우수
mIoU (ADE20K): 37.4
```

---

## 3. QLoRA 파인튜닝 설정 (M5 24GB 최적화)

### 3-1. 환경 설치
```bash
pip install transformers datasets peft accelerate
pip install segmentation-models-pytorch   # 보조 유틸리티
pip install matplotlib opencv-python      # 시각화
```

### 3-2. SegFormer QLoRA 설정
```python
from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    # MiT(Mix Transformer) Encoder의 어텐션 레이어
    target_modules=[
        "attention.self.query",
        "attention.self.value",
    ],
    lora_dropout=0.1,
    bias="none",
    task_type="SEMANTIC_SEGMENTATION"
)

model = SegformerForSemanticSegmentation.from_pretrained(
    "nvidia/segformer-b2-finetuned-ade-512-512",
    num_labels=<YOUR_CLASS_COUNT>,          # 커스텀 클래스 수
    ignore_mismatched_sizes=True,           # 헤드 재초기화
    torch_dtype=torch.float16,
    device_map="mps"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# 예상: trainable 약 440K / 27M (1.6%)
```

### 3-3. 학습 설정
```python
training_args = TrainingArguments(
    output_dir="./segformer-finetuned",
    per_device_train_batch_size=16,   # 512×512, M5 24GB
    gradient_accumulation_steps=2,
    num_train_epochs=100,
    learning_rate=6e-5,
    fp16=True,
    lr_scheduler_type="polynomial",   # 분할 태스크에 효과적
    save_strategy="epoch",
    metric_for_best_model="mean_iou",
)
```

### 3-4. mIoU 평가 메트릭
```python
import evaluate
metric = evaluate.load("mean_iou")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    logits_tensor = torch.from_numpy(logits)
    # 업샘플링: 모델 출력(128×128) → 레이블 크기(512×512)
    upsampled = nn.functional.interpolate(
        logits_tensor, size=labels.shape[-2:], mode="bilinear"
    )
    predicted = upsampled.argmax(dim=1).numpy()
    return metric.compute(
        predictions=predicted,
        references=labels,
        num_labels=<YOUR_CLASS_COUNT>,
        ignore_index=255
    )
```

---

## 4. 멀티에이전트 역할 정의

```yaml
agent_id: segmentation_agent
role: "픽셀 단위 영역 분할"
input:
  - type: image
    format: [jpg, png]
    size: 512x512
  - type: bounding_boxes    # detection_agent 결과 (선택적 ROI 집중)
    format: List[{x, y, w, h}]
output:
  - segmentation_mask: tensor[H, W]    # 픽셀별 클래스 ID
  - class_areas: Dict[str, float]      # 클래스별 면적 비율
  - overlay_image: PIL.Image           # 시각화용
downstream_agents:
  - anomaly_agent     # 분할 영역 이상 탐지
  - nlp_agent         # 영역 설명 생성 (캡셔닝 연계)
upstream_agents:
  - detection_agent   # ROI 좌표 수신
```

---

## 5. 최적화 툴 & 스킬

### 필수 툴
| 툴 | 용도 | 설치 |
|----|------|------|
| `segmentation-models-pytorch` | 손실함수·디코더 유틸 | `pip install segmentation-models-pytorch` |
| `labelme` | 시멘틱 마스크 라벨링 | `pip install labelme` |
| `pycocotools` | COCO 포맷 마스크 처리 | `pip install pycocotools` |
| `kornia` | 미분가능 이미지 처리 | `pip install kornia` |

### 시각화 유틸리티
```python
import numpy as np
import matplotlib.pyplot as plt

def visualize_segmentation(image, mask, palette, alpha=0.5):
    """분할 마스크 오버레이 시각화"""
    colored_mask = np.zeros((*mask.shape, 3), dtype=np.uint8)
    for class_id, color in enumerate(palette):
        colored_mask[mask == class_id] = color
    
    overlay = (np.array(image) * (1 - alpha) + colored_mask * alpha).astype(np.uint8)
    return PIL.Image.fromarray(overlay)
```

### 추천 스킬 체크리스트
- [ ] ADE20K 150개 클래스 → 커스텀 클래스 매핑
- [ ] 클래스 불균형 처리 (픽셀 가중치 설정)
- [ ] 딜레이티드 어텐션 vs. 일반 어텐션 비교
- [ ] 멀티스케일 추론 (sliding window) 구현
- [ ] ONNX 변환으로 에지 배포 최적화

---

## 6. 성능 벤치마크 예상치 (M5 24GB)

| 작업 | 예상 수치 |
|------|----------|
| 단일 이미지 추론 (512×512) | ~18ms |
| QLoRA 학습 (1 epoch, 20k 이미지) | ~45분 |
| 모델 로드 시간 | ~3초 |
| GPU 메모리 사용 | ~3.5GB (fp16) |

---

## 7. 도메인별 사전학습 모델 선택 가이드

```
자율주행 데이터 → nvidia/segformer-b2-finetuned-cityscapes-1024-1024
의료 이미지     → 커스텀 파인튜닝 (ADE20K 베이스)
위성 이미지     → nvidia/segformer-b5-finetuned-ade-640-640
실시간 처리     → nvidia/segformer-b0-finetuned-ade-512-512
```
