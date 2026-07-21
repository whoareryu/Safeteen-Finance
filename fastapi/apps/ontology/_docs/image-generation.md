# Agent 05 — GAN 이미지 생성
> **원본 모델**: DCGAN, Self-Attention GAN (SAGAN)  
> **대체 모델**: Stable Diffusion XL Turbo + LoRA / LCM  
> **환경**: MacBook M5 · 24GB Unified Memory

---

## 1. 왜 DCGAN/SAGAN을 대체하는가?

| 항목 | DCGAN | SAGAN | SDXL Turbo + LoRA (대체) |
|------|-------|-------|--------------------------|
| 생성 품질 | 낮음 | 중간 | 매우 높음 |
| 학습 안정성 | Mode collapse 빈번 | 중간 | 높음 (Diffusion) |
| 컨트롤 가능성 | 없음 | 없음 | 텍스트·이미지 프롬프트 |
| M5 생성 속도 | 빠름 | 중간 | 1~4 step (Turbo) |
| 파인튜닝 방식 | 전체 재학습 | 전체 재학습 | LoRA (효율적) |
| 커뮤니티 생태계 | 작음 | 작음 | 매우 큼 |

---

## 2. 추천 모델 상세

### 기본 추천: `stabilityai/sdxl-turbo`
```
허깅페이스 ID : stabilityai/sdxl-turbo
파라미터     : 3.5B (UNet + VAE + CLIP)
생성 스텝    : 1~4 step (Adversarial Diffusion Distillation)
출력 해상도  : 512×512 (기본), 1024×1024 가능
라이선스     : SDXL Turbo Research License
메모리 사용  : ~8GB fp16
```

### 경량 대안: `stabilityai/stable-diffusion-2-1`
```
파라미터 : 865M
해상도   : 768×768
라이선스 : CreativeML OpenRAIL-M
메모리   : ~4.5GB fp16
특징     : M5 24GB에서 여유 있게 실행
```

### 최경량 (빠른 프로토타입): LCM-LoRA + SD 1.5
```
허깅페이스 ID : latent-consistency/lcm-lora-sdv1-5
생성 스텝    : 2~8 step
메모리       : ~3GB fp16
속도         : ~0.5초/이미지 (M5 MPS)
```

---

## 3. LoRA 파인튜닝 설정 (M5 24GB 최적화)

### 3-1. 환경 설치
```bash
pip install diffusers transformers accelerate peft
pip install xformers   # 어텐션 최적화 (M5에서 효과 제한적)
pip install torch      # MPS 지원 버전
```

### 3-2. SDXL LoRA 학습 (DreamBooth 방식)
```bash
# 허깅페이스 공식 학습 스크립트 사용
accelerate launch train_dreambooth_lora_sdxl.py \
  --pretrained_model_name_or_path="stabilityai/sdxl-turbo" \
  --instance_data_dir="./my_images" \
  --output_dir="./sdxl-lora-finetuned" \
  --instance_prompt="a photo of sks style" \
  --rank=4 \
  --resolution=512 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --learning_rate=1e-4 \
  --lr_scheduler="constant" \
  --mixed_precision="fp16" \
  --max_train_steps=500
```

### 3-3. Python 코드로 LoRA 학습
```python
from diffusers import StableDiffusionXLPipeline
from peft import LoraConfig
import torch

# SDXL UNet에 LoRA 적용
lora_config = LoraConfig(
    r=4,
    lora_alpha=4,
    init_lora_weights="gaussian",
    target_modules=["to_k", "to_q", "to_v", "to_out.0"],
)

pipeline = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/sdxl-turbo",
    torch_dtype=torch.float16
).to("mps")

# UNet에 LoRA 어댑터 추가
pipeline.unet.add_adapter(lora_config)
```

### 3-4. 추론 (1~4 step 생성)
```python
from diffusers import AutoPipelineForText2Image
import torch

pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sdxl-turbo",
    torch_dtype=torch.float16,
    variant="fp16"
).to("mps")

# LoRA 어댑터 로드
pipe.load_lora_weights("./sdxl-lora-finetuned")

# 1-step 생성 (Turbo 특성)
image = pipe(
    prompt="a beautiful landscape with mountains",
    num_inference_steps=1,
    guidance_scale=0.0    # Turbo는 CFG 0 권장
).images[0]
image.save("generated.png")
```

---

## 4. 멀티에이전트 역할 정의

```yaml
agent_id: generation_agent
role: "조건부 이미지 생성 & 스타일 변환"
input:
  - type: text_prompt
    format: str
  - type: reference_image    # Image-to-Image 변환 (선택)
    format: PIL.Image
  - type: segmentation_mask  # 영역별 생성 제어 (선택)
    source: segmentation_agent
output:
  - generated_image: PIL.Image
  - generation_metadata: {prompt, seed, steps, model}
  - image_tensor: tensor     # 다운스트림 에이전트용
downstream_agents:
  - anomaly_agent    # 생성 이미지의 이상 여부 확인
  - classification_agent  # 생성 결과 검증
upstream_agents:
  - segmentation_agent    # 마스크 기반 inpainting
  - nlp_agent            # 텍스트 프롬프트 최적화
```

---

## 5. 최적화 툴 & 스킬

### 필수 툴
| 툴 | 용도 | 설치 |
|----|------|------|
| `diffusers` | SDXL 파이프라인 허브 | `pip install diffusers` |
| `kohya-ss` | GUI 기반 LoRA 학습 | GitHub 클론 |
| `compel` | 프롬프트 가중치 설정 | `pip install compel` |
| `invisible-watermark` | 생성 이미지 워터마크 | `pip install invisible-watermark` |

### 고급 제어: ControlNet 연계
```python
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel

# Pose → 이미지 생성 (pose_agent 연계)
controlnet = ControlNetModel.from_pretrained(
    "thibaud/controlnet-openpose-sdxl-1.0",
    torch_dtype=torch.float16
)

pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    controlnet=controlnet,
    torch_dtype=torch.float16
).to("mps")

# pose_agent 출력 스켈레톤 이미지를 조건으로 사용
image = pipe(
    prompt="person in a yoga pose, studio lighting",
    image=skeleton_image,  # pose_agent 출력
    controlnet_conditioning_scale=0.5
).images[0]
```

### 추천 스킬 체크리스트
- [ ] CFG Scale 이해 (Turbo: 0, 일반: 7~12)
- [ ] CLIP 임베딩 조작으로 스타일 혼합
- [ ] Negative prompt 전략 (품질 향상)
- [ ] Inpainting으로 segmentation 마스크 활용
- [ ] LoRA 여러 개 동시 로드 (알파 가중치 조합)
- [ ] NSFW 필터 구현 (안전 배포)

---

## 6. 성능 벤치마크 예상치 (M5 24GB)

| 작업 | 예상 수치 |
|------|----------|
| 1-step 생성 (512×512, Turbo) | ~0.8초 |
| 4-step 생성 (512×512, Turbo) | ~2.5초 |
| LoRA 학습 (500 steps) | ~25분 |
| 모델 로드 시간 | ~8초 |
| 메모리 사용 (fp16) | ~8GB |

---

## 7. GAN vs Diffusion 비교 정리

```
DCGAN 장점  : 빠른 학습, 단순한 구조
DCGAN 단점  : Mode collapse, 품질 제한, 컨트롤 불가

SDXL 장점   : 고품질, 텍스트 컨트롤, 활발한 생태계
SDXL 단점   : 무거운 모델, 추론 속도 (Turbo로 보완)

→ M5 24GB + Turbo 조합이 실용성 최고
```
