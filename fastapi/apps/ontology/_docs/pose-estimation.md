# Agent 04 — 자세 추정 (Pose Estimation)
> **원본 모델**: OpenPose  
> **대체 모델**: ViTPose-B (Vision Transformer for Pose) + QLoRA  
> **환경**: MacBook M5 · 24GB Unified Memory

---

## 1. 왜 OpenPose를 대체하는가?

| 항목 | OpenPose | ViTPose-B (대체) |
|------|----------|-----------------|
| 아키텍처 | CNN (VGG 백본) | ViT-Base |
| AP (COCO) | 61.8 | 75.8 |
| 라이선스 | Non-commercial | Apache 2.0 |
| Multi-person | PAF 기반 (느림) | Top-down (빠름) |
| 키포인트 수 | 18 | 17 (COCO) / 133 (WholeBody) |
| QLoRA 적용 | 불가 | 가능 |
| M5 호환성 | 제한적 | MPS 완전 지원 |

---

## 2. 추천 모델 상세

### 기본 추천: `usehttps/ViTPose-B-simple-coco`
```
허깅페이스 ID : nielsr/ViTPose_base_simple_coco
파라미터     : 86M
AP (COCO)   : 75.8
키포인트     : 17 (COCO 표준)
입력         : Person crop → 256×192
라이선스     : Apache 2.0
```

### 전신 추정 대안: WholeBody ViTPose
```
키포인트: 133개 (얼굴 68 + 손 42 + 발 6 + 몸 17)
용도: 댄스 분석, 수어 인식, 상세 동작 분석
파라미터: 307M (ViTPose-H 기반)
```

### 경량 대안 (실시간): MoveNet Lightning
```
파라미터 : ~3M (TFLite)
키포인트  : 17
특징      : 30 FPS 이상 실시간 처리, TF Lite로 M5 최적화
한계      : QLoRA 파인튜닝 불가 (TF 모델)
```

---

## 3. QLoRA 파인튜닝 설정 (M5 24GB 최적화)

### 3-1. 환경 설치
```bash
pip install transformers datasets peft accelerate
pip install mmpose mmcv    # ViTPose 공식 지원 프레임워크
# 또는 허깅페이스 transformers 직접 사용
```

### 3-2. ViTPose QLoRA 설정
```python
# 허깅페이스 transformers 방식
from transformers import ViTPoseForPoseEstimation, ViTPoseImageProcessor
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    # ViT-Base attention 레이어
    target_modules=["query", "value"],
    lora_dropout=0.1,
    bias="none",
    # 키포인트 회귀 태스크
    task_type="TOKEN_CLASSIFICATION"
)

model = ViTPoseForPoseEstimation.from_pretrained(
    "nielsr/ViTPose_base_simple_coco",
    torch_dtype=torch.float16,
    device_map="mps"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# 예상: trainable 약 589K / 86M (0.68%)
```

### 3-3. 파이프라인: Top-down 방식
```python
# Step 1: detection_agent로 사람 감지 → BBox 획득
# Step 2: BBox crop → ViTPose 입력
def pose_pipeline(image, bboxes):
    """Top-down pose estimation pipeline"""
    all_keypoints = []
    processor = ViTPoseImageProcessor.from_pretrained("nielsr/ViTPose_base_simple_coco")
    
    for bbox in bboxes:
        # 사람 영역 크롭 + 패딩
        person_crop = crop_and_pad(image, bbox, target_size=(256, 192))
        inputs = processor(images=person_crop, return_tensors="pt").to("mps")
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        keypoints = outputs.pose_logits  # [1, 17, 64, 48] heatmap
        coords = heatmap_to_coords(keypoints, original_bbox=bbox)
        all_keypoints.append(coords)
    
    return all_keypoints   # [[x,y,conf] × 17] × 사람 수
```

### 3-4. 커스텀 키포인트 포맷
```python
COCO_KEYPOINTS = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

SKELETON_CONNECTIONS = [
    (0, 1), (0, 2), (1, 3), (2, 4),           # 얼굴
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # 팔
    (5, 11), (6, 12), (11, 12),                # 몸통
    (11, 13), (13, 15), (12, 14), (14, 16),   # 다리
]
```

---

## 4. 멀티에이전트 역할 정의

```yaml
agent_id: pose_agent
role: "인체 관절 키포인트 추출 & 자세 분류"
input:
  - type: image
    format: [jpg, png]
  - type: person_bboxes      # detection_agent에서 전달
    format: List[{x, y, w, h}]
output:
  - keypoints: List[{name, x, y, confidence}]  # 17 × 사람 수
  - pose_category: str       # standing/sitting/walking/...
  - skeleton_image: PIL.Image
  - action_features: tensor  # 하류 분석용 특징 벡터
downstream_agents:
  - nlp_agent        # 자세 설명 생성
  - anomaly_agent    # 비정상 자세 감지 (낙상 감지 등)
upstream_agents:
  - detection_agent  # 사람 BBox 수신
```

---

## 5. 최적화 툴 & 스킬

### 필수 툴
| 툴 | 용도 | 설치 |
|----|------|------|
| `mmpose` | ViTPose 공식 프레임워크 | `pip install mmpose` |
| `xtcocotools` | COCO 키포인트 평가 | `pip install xtcocotools` |
| `mediapipe` | 경량 실시간 대안 | `pip install mediapipe` |
| `pykinect-azure` | Kinect 연동 (3D 확장) | 별도 설치 |

### 자세 분류 후처리 (규칙 기반)
```python
def classify_pose(keypoints: dict) -> str:
    """키포인트 → 자세 카테고리 분류"""
    left_hip_y = keypoints["left_hip"][1]
    left_knee_y = keypoints["left_knee"][1]
    left_ankle_y = keypoints["left_ankle"][1]
    
    # 무릎 굽힘 각도 계산
    knee_angle = calculate_angle(
        keypoints["left_hip"], 
        keypoints["left_knee"], 
        keypoints["left_ankle"]
    )
    
    if knee_angle < 90:
        return "sitting"
    elif left_hip_y > left_ankle_y:
        return "lying"
    else:
        return "standing"
```

### 추천 스킬 체크리스트
- [ ] Heatmap → 좌표 변환 (argmax + 서브픽셀 정밀도)
- [ ] OKS (Object Keypoint Similarity) 평가 구현
- [ ] 시계열 키포인트로 동작 인식 (LSTM 연계)
- [ ] 스켈레톤 정규화 (신체 비율 독립화)
- [ ] 낙상 감지 규칙 설계 (실버케어 응용)

---

## 6. 성능 벤치마크 예상치 (M5 24GB)

| 작업 | 예상 수치 |
|------|----------|
| 단일 인물 추론 | ~15ms |
| 다중 인물 (5명) 추론 | ~75ms |
| QLoRA 학습 (1 epoch, 10k 이미지) | ~30분 |
| 모델 로드 시간 | ~3초 |

---

## 7. 응용 시나리오

```
스포츠 분석  → 골프 스윙 교정, 달리기 자세 분석
재활 의료    → 물리치료 자세 모니터링
스마트홈     → 낙상 감지, 수면 자세 분석 (살핌/PawLog 연계 가능)
댄스/공연    → 안무 기록, 동작 채점
```
