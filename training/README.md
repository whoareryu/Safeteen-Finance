# EXAONE-3.5-2.4B-Instruct QLoRA 파인튜닝

메인 화면 채팅(`/api/plant/chat`)이 쓰는 exaone3.5:2.4b(Ollama)와는 별도로,
이 폴더는 **QLoRA로 어댑터를 학습**하기 위한 독립 환경이다.

- 서빙(`fastapi/`)과 완전히 분리 — Docker 빌드 컨텍스트(`./fastapi`) 밖이라 프로덕션
  이미지에 절대 포함되지 않는다.
- **원격 PC(RTX 3050, CUDA)에서만 실행 가능.** bitsandbytes 4bit 양자화는 CUDA 전용이라
  로컬 맥(Apple Silicon)에서는 학습이 안 된다. Ollama 서빙은 그대로 원격 WSL 호스트에서
  돌고, 이 학습 venv는 별개로 같은 호스트에 둔다.

## 1. 원격 PC에 학습 전용 venv 만들기

```bash
cd ~/projects/cloud.whoareryu/training
python3 -m venv .venv
source .venv/bin/activate

# torch는 드라이버(CUDA 12.6)에 맞는 빌드를 먼저 명시적으로 설치한다.
# 기본 PyPI 인덱스로 설치하면 최신 CUDA(13.x) 번들이 딸려와서
# "driver too old" 에러가 난다. 드라이버 버전은 nvidia-smi로 확인.
pip install torch --index-url https://download.pytorch.org/whl/cu126

pip install -r requirements.txt
```

`/tmp`가 작은 tmpfs(WSL 기본 3.9GB)라 큰 wheel(torch 등) 다운로드 중
"No space left on device"가 날 수 있다. 그럴 땐 임시 디렉터리를 큰 디스크로 돌린다:

```bash
mkdir -p .pip-tmp
TMPDIR=./.pip-tmp pip install ...
```

## 2. 원본(비양자화) 베이스 모델 받기

QLoRA는 학습 시점에 bitsandbytes로 4bit 양자화하므로, **AWQ 등 사전 양자화된 버전이 아닌
원본 체크포인트**가 필요하다.

```bash
huggingface-cli download LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct \
  --local-dir ./models/EXAONE-3.5-2.4B-Instruct
```

## 3. 학습 데이터 준비

`data/train.jsonl` — 한 줄에 하나씩 완성된 학습 텍스트:

```json
{"text": "[|system|]...[|user|]...[|assistant|]..."}
```

EXAONE 프롬프트 포맷은 `modeling_exaone.py`가 아니라 tokenizer의 chat template
(`tokenizer.apply_chat_template`)을 따르는 것을 권장한다.

## 4. 학습 실행

```bash
python train_qlora.py \
  --base-model ./models/EXAONE-3.5-2.4B-Instruct \
  --dataset ./data/train.jsonl \
  --output-dir ./outputs/exaone-2.4b-qlora
```

결과물은 LoRA 어댑터(수십~수백 MB)만 `outputs/`에 저장된다. 베이스 모델 가중치는
그대로 두고 어댑터만 얹는 방식이라, 서빙 쪽 Ollama exaone 모델과는 독립적으로 관리된다.

## 참고

- `.venv/`, `models/`, `outputs/`, `data/`는 전부 `.gitignore` 처리됨 (수 GB 단위라
  git으로 관리하지 않는다).
- 학습된 어댑터를 실제 서빙(Ollama)에 반영하려면 별도로 병합(`merge_and_unload`) 후
  Ollama Modelfile로 재패키징하는 과정이 필요 — 아직 이 단계는 구현 안 됨.
