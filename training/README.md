# EXAONE-3.5-2.4B-Instruct QLoRA 파인튜닝

메인 화면 채팅(`/api/plant/chat`)이 쓰는 exaone3.5:2.4b(Ollama)와는 별도로,
이 폴더는 **QLoRA로 어댑터를 학습**하기 위한 독립 환경이다.

- 서빙(`fastapi/`)과 완전히 분리 — Docker 빌드 컨텍스트(`./fastapi`) 밖이라 프로덕션
  이미지에 절대 포함되지 않는다.
- **원격 PC(RTX 3050, CUDA)에서만 실행 가능.** bitsandbytes 4bit 양자화는 CUDA 전용이라
  로컬 맥(Apple Silicon)에서는 학습이 안 된다. Ollama 서빙은 그대로 원격 WSL 호스트에서
  돌고, 이 학습 venv는 별개로 같은 호스트에 둔다.

## 1. 원격 PC에 학습 전용 venv 만들기

원격 PC는 Ubuntu 26.04(WSL2)라 시스템 기본 Python이 3.14인데, 이 버전은 ML
생태계 wheel(구버전 `tokenizers`, CUDA 맞춤 `torch` 등)이 아직 부족해 설치가
깨진다. `uv`로 Python 3.11(prebuilt, 컴파일/sudo 불필요)을 따로 설치해 그걸로
venv를 만든다.

```bash
cd ~/projects/cloud.whoareryu/training
uv python install 3.11
~/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11 -m venv .venv
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

torch의 일부 연산(예: RoPE)은 최초 실행 시 Triton 커널을 즉석 컴파일하는데, C
컴파일러가 없으면 `Failed to find C compiler`로 죽는다. 없다면 설치한다:

```bash
sudo apt install -y build-essential
```

## 2. 원본(비양자화) 베이스 모델 받기

QLoRA는 학습 시점에 bitsandbytes로 4bit 양자화하므로, **AWQ 등 사전 양자화된 버전이 아닌
원본 체크포인트**가 필요하다. (`huggingface-cli`는 deprecated — `hf` CLI를 쓴다.)

```bash
hf download LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct \
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
- **버전 조합**: `transformers>=5.0,<6.0` + `peft==0.13.2` + `trl>=1.0,<2.0`.
  EXAONE 저장소의 `trust_remote_code` 커스텀 코드(`modeling_exaone.py`)가
  `configuration_exaone.py`의 `RopeParameters` 등 v5 전용 심볼을 쓰도록
  업데이트되어 있어 transformers 4.x로는 아예 로드가 안 된다(README의
  "v4.43 이상" 안내는 stale). peft는 0.13.x가 아니면 `get_peft_model()` 단계에서
  `get_input_embeddings` 관련 하드 에러가 난다.
- **`train_qlora.py`에 박혀 있는 호환 셔밈 2개**: EXAONE의 trust_remote_code가
  일부 transformers 내부 API를 구버전 시그니처로 호출해서(모델 리포 쪽 코드가
  살아있는 채로 계속 업데이트되며 API가 어긋난 것), 스크립트 안에서 직접
  보정한다.
  1. `create_causal_mask()` 호출을 `input_embeds=`(단수)로 하는데 실제
     파라미터명은 `inputs_embeds=`(복수)이고 `cache_position=` 인자는 아예
     없음 — 감싸서 이름 변환 + 미지원 kwarg 제거.
  2. `ExaoneForCausalLM`의 백본 속성명이 `self.transformer`인데 transformers
     5.x의 `get_input_embeddings()` 자동탐지는 `self.model`만 찾아서
     `NotImplementedError`가 나고, 이 때문에 `get_output_embeddings()`도
     `None`을 반환해 trl이 `lm_head.weight`에서 죽음 — 인스턴스에
     `model.transformer.wte` / `model.lm_head`를 직접 바인딩해서 우회.
