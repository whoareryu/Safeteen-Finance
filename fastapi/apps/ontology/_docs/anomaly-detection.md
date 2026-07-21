# Agent 06 — GAN 이상 화상 탐지 (Anomaly Detection)
> **원본 모델**: AnoGAN, Efficient GAN-Based Anomaly Detection  
> **대체 모델**: FastFlow + PatchCore (Normalizing Flow 기반)  
> **환경**: MacBook M5 · 24GB Unified Memory

---

## 1. 왜 AnoGAN/EfficientGAN을 대체하는가?

| 항목 | AnoGAN | EfficientGAN | FastFlow + PatchCore (대체) |
|------|--------|--------------|-----------------------------|
| 학습 안정성 | 낮음 (GAN 불안정) | 중간 | 높음 (Flow 기반) |
| 추론 속도 | 매우 느림 (역전파 반복) | 느림 | 실시간 가능 |
| AUROC (MVTec) | 74.5 | 82.7 | 98.4 (PatchCore) |
| 이상 위치화 | 불가 | 불가 | 가능 (픽셀 단위) |
| 정상 샘플만 필요 | O | O | O (이상 샘플 불필요) |
| QLoRA 적용 | 불가 | 불가 | ViT 백본에 LoRA 적용 가능 |

---

## 2. 추천 모델 상세

### 기본 추천: `anomalib` PatchCore
```
라이브러리  : anomalib (Intel OpenVINO)
알고리즘    : PatchCore (Memory Bank 방식)
AUROC       : 99.1% (MVTec AD 기준)
학습 방식   : 정상 샘플만으로 Memory Bank 구축
특징        : 학습 없이 바로 적용 가능, 이상 히트맵 제공
라이선스    : Apache 2.0
```

### 속도 우선: `FastFlow`
```
알고리즘   : Normalizing Flow (2D)
AUROC      : 98.4% (MVTec)
추론 속도  : 21.8 FPS (M5 기준)
백본       : WideResNet-50 또는 ViT
특징       : 픽셀 단위 이상 지도 생성
```

### LoRA 파인튜닝 연계: `WinCLIP`
```
기반       : CLIP ViT-B/32 + LoRA
AUROC      : 91.8% (zero-shot)
특징       : 텍스트 프롬프트로 이상 유형 지정 가능
예시       : "crack", "scratch", "discoloration"
```

---

## 3. 설치 및 기본 사용 (anomalib 기준)

### 3-1. 환경 설치
```bash
pip install anomalib[full]   # PatchCore, FastFlow 등 포함
pip install torch torchvision
```

### 3-2. PatchCore 이상 탐지 (코드 최소화)
```python
from anomalib.data import Folder
from anomalib.models import Patchcore
from anomalib.engine import Engine

# 데이터셋 구성 (정상 샘플만 train에 위치)
# dataset/
#   train/good/   ← 정상 이미지
#   test/good/    ← 정상 테스트
#   test/defect/  ← 이상 테스트

datamodule = Folder(
    root="./dataset",
    normal_dir="train/good",
    abnormal_dir="test/defect",
    image_size=(256, 256)
)

model = Patchcore(
    backbone="wide_resnet50_2",
    layers=["layer2", "layer3"],
    coreset_sampling_ratio=0.1,    # 메모리 절약
    num_neighbors=9
)

engine = Engine(
    accelerator="mps",             # M5 Metal 가속
    max_epochs=1                   # PatchCore는 1 epoch
)
engine.fit(model=model, datamodule=datamodule)
```

### 3-3. WinCLIP + LoRA 파인튜닝 방식
```python
from transformers import CLIPModel, CLIPProcessor
from peft import LoraConfig, get_peft_model

# CLIP ViT-B에 LoRA 적용
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],  # Vision Encoder
    lora_dropout=0.1,
    bias="none"
)

clip_model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32",
    torch_dtype=torch.float16,
    device_map="mps"
)
clip_model = get_peft_model(clip_model, lora_config)

# 이상 프롬프트 정의
ANOMALY_PROMPTS = [
    "a photo of a {defect_type} on the surface",
    "a photo of a product with {defect_type}",
    "a defective product showing {defect_type}"
]
NORMAL_PROMPTS = [
    "a photo of a normal product",
    "a photo of a good quality item"
]

def compute_anomaly_score(image, defect_types=["crack", "scratch"]):
    """텍스트 프롬프트 기반 이상 점수 계산"""
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    prompts = NORMAL_PROMPTS + [
        p.format(defect_type=d) for d in defect_types for p in ANOMALY_PROMPTS
    ]
    
    inputs = processor(
        text=prompts, images=image, return_tensors="pt", padding=True
    ).to("mps")
    
    outputs = clip_model(**inputs)
    logits = outputs.logits_per_image[0]
    
    normal_score = logits[:len(NORMAL_PROMPTS)].mean()
    anomaly_score = logits[len(NORMAL_PROMPTS):].mean()
    
    return float(anomaly_score - normal_score)  # 양수 → 이상
```

### 3-4. 이상 히트맵 시각화
```python
from anomalib.visualization import Visualizer

def visualize_anomaly(image, anomaly_map, threshold=0.5):
    """이상 위치 히트맵 오버레이"""
    import cv2
    import numpy as np
    
    # 정규화된 이상 점수 맵
    heatmap = (anomaly_map - anomaly_map.min()) / (anomaly_map.max() - anomaly_map.min())
    heatmap_colored = cv2.applyColorMap(
        (heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET
    )
    
    # 원본 이미지와 오버레이
    image_np = np.array(image)
    overlay = cv2.addWeighted(image_np, 0.6, heatmap_colored, 0.4, 0)
    
    # 이상 영역 바운딩박스 (임계값 초과)
    binary_mask = (heatmap > threshold).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)
    
    return overlay, float(anomaly_map.max())   # 이미지, 최고 이상 점수
```

---

## 4. 멀티에이전트 역할 정의

```yaml
agent_id: anomaly_agent
role: "이상 화상 탐지 & 품질 검사"
input:
  - type: image
    format: [jpg, png]
  - type: segmentation_mask    # segmentation_agent 결과 (선택)
  - type: class_label          # classification_agent 결과 (도메인 특화)
  - type: defect_type_hints    # nlp_agent가 제공하는 이상 유형 텍스트
output:
  - is_anomaly: bool
  - anomaly_score: float       # 0~1
  - anomaly_map: tensor[H, W]  # 픽셀별 이상 강도
  - anomaly_bbox: List[{x, y, w, h}]
  - defect_category: str       # "crack", "scratch", "normal"
downstream_agents:
  - nlp_agent      # 이상 리포트 생성
upstream_agents:
  - classification_agent   # 검사 대상 카테고리 수신
  - segmentation_agent     # 관심 영역 마스크 수신
  - generation_agent       # 합성 이상 샘플 (데이터 증강)
```

---

## 5. 최적화 툴 & 스킬

### 필수 툴
| 툴 | 용도 | 설치 |
|----|------|------|
| `anomalib` | 이상 탐지 통합 프레임워크 | `pip install anomalib[full]` |
| `opencv-python` | 이상 시각화 | `pip install opencv-python` |
| `scikit-learn` | AUROC, F1 평가 | `pip install scikit-learn` |
| `grad-cam` | 이상 설명 가능성 | `pip install grad-cam` |

### 데이터 전략 (정상 샘플만 수집)
```python
# 이상 탐지는 정상 데이터만 있으면 됨!
# 추천 공개 데이터셋:
# - MVTec AD: 제조업 결함 (15 카테고리)
# - BTAD: 3개 산업 제품
# - VisA: 12개 제품 카테고리

# 데이터 증강으로 이상 샘플 합성 (generation_agent 활용)
# → SDXL + ControlNet으로 결함 이미지 생성 → 검증 데이터로 활용
```

### 추천 스킬 체크리스트
- [ ] MVTec AD로 베이스라인 AUROC 측정
- [ ] PatchCore Memory Bank 크기 조절 (속도-정확도 트레이드오프)
- [ ] generation_agent 합성 이상 샘플로 검증 세트 구축
- [ ] 이상 임계값 도메인 최적화 (precision-recall 커브)
- [ ] ONNX 변환 후 엣지 배포 (품질 검사 라인)

---

## 6. 성능 벤치마크 예상치 (M5 24GB)

| 모델 | AUROC (MVTec) | 추론 속도 | 메모리 |
|------|--------------|----------|--------|
| AnoGAN (원본) | 74.5% | 5 FPS | 6GB |
| PatchCore | 99.1% | 15 FPS | 4GB |
| FastFlow | 98.4% | 22 FPS | 3GB |
| WinCLIP+LoRA | 91.8% | 25 FPS | 5GB |
