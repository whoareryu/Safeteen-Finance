# Agent 07 — 자연어 처리 감정 분석 (NLP Sentiment Analysis)
> **원본 모델**: Transformer (BERT 기반 감정 분석)  
> **대체 모델**: KLUE-RoBERTa-large + QLoRA (한국어 특화)  
> **환경**: MacBook M5 · 24GB Unified Memory

---

## 1. 왜 일반 Transformer를 대체하는가?

| 항목 | 일반 BERT-base | KLUE-RoBERTa-large (대체) |
|------|---------------|--------------------------|
| 한국어 성능 | 낮음 (영어 사전학습) | 높음 (한국어 전용) |
| 감정 분석 F1 | ~78% | ~91.2% |
| 형태소 처리 | 미지원 | 한국어 서브워드 최적화 |
| QLoRA 적용 | 가능 | 가능 |
| 파라미터 수 | 110M | 338M |
| 추론 속도 (M5) | 빠름 | 중간 |

---

## 2. 추천 모델 상세

### 기본 추천 (한국어): `klue/roberta-large`
```
허깅페이스 ID : klue/roberta-large
파라미터     : 338M
KLUE NST F1  : 91.2
사전학습 데이터: 62GB 한국어 텍스트
라이선스     : CC BY 4.0
```

### 경량 대안 (한국어): `klue/roberta-base`
```
허깅페이스 ID : klue/roberta-base
파라미터     : 111M
KLUE NST F1  : 88.1
특징         : M5에서 실시간 추론, 메모리 2GB 이하
```

### 멀티태스크 대안: `snunlp/KR-ELECTRA-discriminator`
```
허깅페이스 ID : snunlp/KR-ELECTRA-discriminator
파라미터     : 110M
특징         : 감정 분석 + 의도 분류 동시 처리 우수
```

### 영어/다국어 필요 시: `cardiffnlp/twitter-roberta-base-sentiment-latest`
```
태스크    : 감정 분석 (Negative/Neutral/Positive)
F1        : 79.6 (English)
특징      : 소셜미디어 특화, 한국어 포함 가능
```

---

## 3. QLoRA 파인튜닝 설정 (M5 24GB 최적화)

### 3-1. 환경 설치
```bash
pip install transformers datasets peft accelerate
pip install konlpy   # 한국어 형태소 분석
pip install kiwipiepy   # 빠른 한국어 토크나이저 (M5 권장)
```

### 3-2. KLUE-RoBERTa QLoRA 설정
```python
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType

# 감정 레이블 정의
SENTIMENT_LABELS = {
    0: "부정",
    1: "중립",
    2: "긍정"
}

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    # RoBERTa Self-Attention 레이어
    target_modules=["query", "value"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.SEQ_CLS
)

tokenizer = AutoTokenizer.from_pretrained("klue/roberta-large")

model = AutoModelForSequenceClassification.from_pretrained(
    "klue/roberta-large",
    num_labels=len(SENTIMENT_LABELS),
    torch_dtype=torch.float16,
    device_map="mps"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# 예상: trainable 약 1.8M / 338M (0.53%)
```

### 3-3. 한국어 데이터 전처리
```python
from datasets import load_dataset

def preprocess_korean(examples):
    """NSMC(네이버 영화 리뷰) 등 한국어 감정 데이터 전처리"""
    # Kiwi 형태소 분석기로 정규화
    from kiwipiepy import Kiwi
    kiwi = Kiwi()
    
    cleaned_texts = []
    for text in examples["document"]:
        # 특수문자 제거 + 형태소 기반 정규화
        result = kiwi.analyze(text)
        morphs = " ".join([token.form for token in result[0].tokens])
        cleaned_texts.append(morphs)
    
    return tokenizer(
        cleaned_texts,
        truncation=True,
        max_length=256,   # 한국어는 128~256으로 충분
        padding="max_length"
    )

# NSMC 데이터셋 로드 (네이버 영화 리뷰 감정)
dataset = load_dataset("nsmc")   # pip install datasets
tokenized = dataset.map(preprocess_korean, batched=True)
```

### 3-4. 학습 설정
```python
from transformers import TrainingArguments, Trainer
import evaluate

training_args = TrainingArguments(
    output_dir="./klue-roberta-sentiment",
    per_device_train_batch_size=32,    # 128토큰, M5 24GB 넉넉
    gradient_accumulation_steps=1,
    num_train_epochs=5,
    learning_rate=2e-4,
    fp16=True,
    warmup_ratio=0.1,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
)

accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"],
        "f1": f1_metric.compute(predictions=predictions, references=labels, average="weighted")["f1"]
    }
```

---

## 4. 멀티에이전트 역할 정의

```yaml
agent_id: nlp_agent
role: "텍스트 감정 분석 & 리포트 생성"
input:
  - type: text
    format: str
    lang: [ko, en]
  - type: image_context        # 다른 에이전트 결과 → 텍스트 설명 생성
    source: [detection_agent, segmentation_agent, anomaly_agent]
output:
  - sentiment: str             # "긍정" / "부정" / "중립"
  - sentiment_score: float     # -1.0 ~ 1.0
  - confidence: float
  - report_text: str           # 비전 에이전트 결과 자연어 설명
  - intent: str                # 의도 분류 (선택)
  - keywords: List[str]        # 핵심 감정 키워드
downstream_agents: []          # 최종 출력 에이전트
upstream_agents:
  - classification_agent   # 이미지 → 텍스트 설명 요청
  - detection_agent        # 감지 결과 → 리포트 생성
  - segmentation_agent     # 분할 결과 → 설명 생성
  - anomaly_agent          # 이상 감지 → 자연어 리포트
  - pose_agent             # 자세 → 동작 설명
  - generation_agent       # 프롬프트 최적화 요청
```

---

## 5. 멀티모달 확장: 이미지 + 텍스트 감정 분석

```python
# 비전 에이전트 결과를 텍스트로 변환 후 감정 분석
def analyze_scene_sentiment(image_results: dict) -> dict:
    """
    다른 에이전트 출력 → 자연어 변환 → 감정 분석
    """
    # 결과 텍스트 조합
    description_parts = []
    
    if "class_label" in image_results:
        description_parts.append(f"이미지에 {image_results['class_label']}가 감지되었습니다.")
    
    if "bounding_boxes" in image_results:
        count = len(image_results["bounding_boxes"])
        description_parts.append(f"총 {count}개의 객체가 발견되었습니다.")
    
    if "is_anomaly" in image_results and image_results["is_anomaly"]:
        score = image_results["anomaly_score"]
        description_parts.append(f"이상 징후가 감지되었습니다 (점수: {score:.2f}).")
    
    if "pose_category" in image_results:
        description_parts.append(f"인물의 자세는 {image_results['pose_category']}입니다.")
    
    scene_text = " ".join(description_parts)
    
    # 감정 분석 실행
    inputs = tokenizer(scene_text, return_tensors="pt", truncation=True, max_length=256).to("mps")
    with torch.no_grad():
        outputs = model(**inputs)
    
    probs = torch.softmax(outputs.logits, dim=-1)[0]
    sentiment_id = probs.argmax().item()
    
    return {
        "input_text": scene_text,
        "sentiment": SENTIMENT_LABELS[sentiment_id],
        "confidence": float(probs[sentiment_id]),
        "scores": {label: float(prob) for label, prob in zip(SENTIMENT_LABELS.values(), probs)}
    }
```

---

## 6. 최적화 툴 & 스킬

### 필수 툴
| 툴 | 용도 | 설치 |
|----|------|------|
| `kiwipiepy` | 한국어 형태소 분석 (빠름) | `pip install kiwipiepy` |
| `soynlp` | 비지도 한국어 토크나이징 | `pip install soynlp` |
| `evaluate` | HuggingFace 평가 지표 | `pip install evaluate` |
| `shap` | 감정 예측 설명 가능성 | `pip install shap` |

### 추천 한국어 감정 데이터셋
```
NSMC          : 네이버 영화 리뷰 (긍/부정, 20만 건)
KSentiment    : 소셜미디어 감정 (5단계)
AIHub 감정말뭉치: 62개 감정 카테고리 (고품질)
KLUE STS      : 문장 유사도 (연계 활용)
```

### 추천 스킬 체크리스트
- [ ] 한국어 특수 처리 (이모지, 자음/모음 단독 표현)
- [ ] 도메인 어댑테이션 (리뷰/SNS/의료 텍스트 차이)
- [ ] 멀티레이블 감정 분류 (복합 감정 처리)
- [ ] Attention 시각화로 감정 근거 추출
- [ ] 스트리밍 추론 (실시간 채팅 감정 모니터링)

---

## 7. 성능 벤치마크 예상치 (M5 24GB)

| 작업 | 예상 수치 |
|------|----------|
| 단일 문장 추론 (128토큰) | ~8ms |
| 배치 추론 (B=64) | ~180ms |
| QLoRA 학습 (1 epoch, NSMC 15만 건) | ~12분 |
| 모델 로드 시간 | ~5초 |
| 메모리 사용 (fp16) | ~2.5GB |
