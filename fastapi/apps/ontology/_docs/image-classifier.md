# CLAUDE.md — ConvNeXt Nano Image Classification Agent

> **Harness Engineering 원칙 적용**: 이 파일은 Claude Code가 프로젝트를 구현할 때 따라야 할 모든 규칙, 구조, 제약을 정의한다.
> 지시를 **추론하거나 생략하지 말 것**. 각 단계를 순서대로 실행하고, 완료 후 다음 단계로 넘어갈 것.

---

## 0. Harness Engineering 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **명시적 계약** | 모든 함수/클래스는 입출력 타입을 명시. 암묵적 의존 금지 |
| **단일 책임** | 파일 하나는 역할 하나. 모델 로직과 라우터 로직은 분리 |
| **검증 우선** | 외부 입력(이미지)은 반드시 진입점에서 검증 후 통과 |
| **실패 명시** | 예외는 삼키지 않는다. 모든 에러는 구체적 메시지와 함께 raise |
| **재현 가능 환경** | `requirements.txt` + `Dockerfile` 없이 구현 완료로 간주하지 않음 |
| **테스트 없이 완료 없음** | 각 레이어(전처리 / 모델 / API)에 대한 단위 테스트 필수 |

---

## 1. 구현 목표

**FastAPI 기반 이미지 분류 API 서버** 구축.
- 클라이언트가 이미지를 `multipart/form-data`로 POST하면
- ConvNeXt Nano (파인튜닝 완료 가중치)가 추론하여
- `{"label": str, "confidence": float}` JSON을 반환한다.

---

## 2. 프로젝트 구조 (이 구조 그대로 생성할 것)

```
project-root/
├── CLAUDE.md                    ← 이 파일
├── requirements.txt
├── Dockerfile
├── class_names.json             ← 커스텀 클래스 목록 (예: ["장미","튤립","해바라기"])
├── weights/
│   └── convnext_nano_ft.pth    ← 파인튜닝 가중치 (사전 준비 필요)
└── app/
    ├── __init__.py
    ├── main.py                  ← FastAPI 앱 진입점 + lifespan
    ├── router.py                ← /classify 엔드포인트
    ├── model.py                 ← 모델 로드 & 추론 클래스
    ├── preprocess.py            ← 이미지 전처리 파이프라인
    ├── schemas.py               ← Pydantic 요청/응답 스키마
    ├── config.py                ← 환경변수 기반 설정값
    └── tests/
        ├── __init__.py
        ├── test_preprocess.py
        ├── test_model.py
        └── test_router.py
```

> **주의**: 위 구조에서 파일/디렉터리를 임의로 추가하거나 병합하지 말 것.

---

## 3. 파일별 구현 명세

### 3-1. `app/config.py`

- `pydantic-settings`의 `BaseSettings`를 사용한다.
- 아래 필드를 환경변수로 읽는다:

```python
class Settings(BaseSettings):
    num_classes: int       # 커스텀 클래스 수
    weights_path: str      # 가중치 파일 경로
    class_names_path: str  # class_names.json 경로
    device: str            # "cpu" | "cuda" | "mps"
    top_k: int = 1         # 반환할 상위 예측 수 (기본 1)

    model_config = SettingsConfigDict(env_file=".env")
```

- `get_settings()` 함수를 `lru_cache`로 감싸 싱글턴으로 제공한다.

---

### 3-2. `app/schemas.py`

```python
from pydantic import BaseModel

class ClassifyResponse(BaseModel):
    label: str
    confidence: float  # 0.0 ~ 1.0, 소수점 4자리

class ErrorResponse(BaseModel):
    detail: str
```

---

### 3-3. `app/preprocess.py`

**규칙**:
- 함수 시그니처: `def preprocess_bytes(image_bytes: bytes) -> torch.Tensor`
- 반환 shape: `(1, 3, 224, 224)` — 배치 차원 포함
- 전처리 순서: `Resize(256)` → `CenterCrop(224)` → `ToTensor()` → `Normalize(ImageNet mean/std)`
- 지원 포맷: JPEG, PNG, WEBP. 그 외 포맷은 `ValueError`를 raise한다.
- PIL 변환 시 반드시 `.convert("RGB")`를 호출한다 (RGBA, 그레이스케일 대응).

**금지사항**:
- 전처리 함수 내부에서 모델 또는 설정값을 직접 import하지 말 것.

---

### 3-4. `app/model.py`

```python
class ClassifierModel:
    def __init__(self, num_classes: int, weights_path: str, device: str): ...
    
    @torch.no_grad()
    def predict(self, tensor: torch.Tensor) -> torch.Tensor:
        # 반환: shape (num_classes,) 확률 벡터 (softmax 적용 후)
        ...
```

**구현 규칙**:
- `timm.create_model("convnext_nano", pretrained=False, num_classes=num_classes)` 사용
- 가중치 로드: `torch.load(weights_path, map_location=device)`
- 로드 후 반드시 `model.eval()` 호출
- `predict()` 는 `@torch.no_grad()` 데코레이터 필수
- 추론 전 tensor를 `self.device`로 이동시킬 것
- 모델 로드 실패 시 `RuntimeError`를 구체적 경로와 함께 raise

**금지사항**:
- `predict()` 내부에서 이미지 파일 I/O 수행 금지
- `predict()` 내부에서 전처리 수행 금지

---

### 3-5. `app/router.py`

```python
router = APIRouter(prefix="/api/v1", tags=["classify"])

@router.post(
    "/classify",
    response_model=ClassifyResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def classify_image(file: UploadFile = File(...)) -> ClassifyResponse:
    ...
```

**구현 규칙**:
- Content-Type 검증: `image/jpeg`, `image/png`, `image/webp` 외 입력은 `HTTPException(400)` 반환
- 파일 크기 제한: 10MB 초과 시 `HTTPException(413)` 반환
- `classifier` 인스턴스는 `request.app.state.classifier`에서 가져온다 (전역변수 사용 금지)
- 예외는 구체적 메시지와 함께 HTTPException으로 변환

**엔드포인트 흐름** (이 순서를 반드시 지킬 것):
```
1. Content-Type 검증
2. 파일 크기 검증
3. 파일 bytes 읽기
4. preprocess_bytes() 호출
5. classifier.predict() 호출
6. top-k argmax로 label & confidence 추출
7. ClassifyResponse 반환
```

---

### 3-6. `app/main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # 1. class_names.json 로드
    # 2. ClassifierModel 초기화
    # 3. app.state에 저장
    app.state.classifier = classifier
    app.state.class_names = class_names
    yield
    # shutdown: 명시적 cleanup 불필요하나 로그 출력

app = FastAPI(
    title="ConvNeXt Nano Classifier",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(router)
```

**금지사항**:
- 모델을 모듈 레벨(함수 밖)에서 초기화하지 말 것
- `@app.on_event` 데코레이터 사용 금지 (deprecated) — `lifespan` 사용

---

## 4. `requirements.txt` (정확히 이 버전을 사용할 것)

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9
torch>=2.2.0
torchvision>=0.17.0
timm>=0.9.16
pillow>=10.3.0
pydantic>=2.7.0
pydantic-settings>=2.2.0
pytest>=8.2.0
httpx>=0.27.0
```

---

## 5. `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**규칙**:
- `weights/` 디렉터리는 COPY 대상에 포함한다.
- `HEALTHCHECK` 명령어를 추가할 것:
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:8000/health || exit 1
  ```
- `/health` 엔드포인트를 `router.py`에 추가할 것 (`{"status": "ok"}` 반환).

---

## 6. 테스트 명세

### `tests/test_preprocess.py`
- `bytes` → tensor shape `(1, 3, 224, 224)` 검증
- 지원 포맷(JPEG, PNG) 각각 테스트
- 비지원 포맷 입력 시 `ValueError` 발생 검증
- RGBA 이미지 입력 시 정상 변환 검증

### `tests/test_model.py`
- 랜덤 가중치로 `ClassifierModel` 초기화 (실제 pth 파일 불필요)
- `predict()` 출력 shape `(num_classes,)` 검증
- `predict()` 출력값 합이 1.0 (±1e-4) 검증 (softmax 확인)

### `tests/test_router.py`
- `httpx.AsyncClient`와 `ASGITransport`로 앱 전체 통합 테스트
- 정상 JPEG 업로드 → 200 응답 검증
- 비이미지 파일 업로드 → 400 응답 검증
- 10MB 초과 파일 업로드 → 413 응답 검증

**테스트 실행 명령어**:
```bash
pytest app/tests/ -v --tb=short
```

---

## 7. 구현 순서 (이 순서대로 진행할 것)

```
Step 1. 프로젝트 구조 생성 (디렉터리 & 빈 파일)
Step 2. requirements.txt, Dockerfile 작성
Step 3. config.py 작성 → .env.example 생성
Step 4. schemas.py 작성
Step 5. preprocess.py 작성 → test_preprocess.py 작성 → pytest 통과 확인
Step 6. model.py 작성 → test_model.py 작성 → pytest 통과 확인
Step 7. router.py 작성
Step 8. main.py 작성
Step 9. test_router.py 작성 → pytest 통과 확인
Step 10. class_names.json 샘플 파일 생성
Step 11. README.md 작성 (실행 방법 포함)
Step 12. Docker 빌드 확인: docker build -t convnext-classifier .
```

> **각 Step 완료 조건**: 해당 단계의 테스트가 존재한다면 pytest가 통과해야 다음 Step으로 넘어간다.

---

## 8. 금지 사항 (절대 위반하지 말 것)

- [ ] 전역 변수로 모델 인스턴스 관리 금지
- [ ] `@app.on_event` 사용 금지
- [ ] `predict()` 내부에서 이미지 파일 직접 열기 금지
- [ ] `try/except pass` 패턴 금지 (예외를 삼키는 빈 핸들러)
- [ ] 하드코딩된 경로 (`"weights/model.pth"` 등) 소스코드 내 직접 작성 금지 → 반드시 `config.py`에서 읽을 것
- [ ] `print()` 디버깅 금지 → `logging` 모듈 사용
- [ ] 테스트 없이 "구현 완료" 보고 금지

---

## 9. `.env.example` (구현 시 생성할 것)

```env
NUM_CLASSES=10
WEIGHTS_PATH=weights/convnext_nano_ft.pth
CLASS_NAMES_PATH=class_names.json
DEVICE=cpu
TOP_K=1
```

---

## 10. 완료 체크리스트

Claude Code는 아래 항목을 모두 확인한 후 완료를 보고한다.

- [ ] `pytest app/tests/ -v` 전체 통과
- [ ] `uvicorn app.main:app --reload` 정상 기동
- [ ] `curl -X POST /api/v1/classify -F "file=@sample.jpg"` 200 응답 확인
- [ ] `curl /health` → `{"status": "ok"}` 확인
- [ ] `docker build -t convnext-classifier .` 성공
- [ ] `requirements.txt` 버전 핀 완료
- [ ] `class_names.json` 샘플 파일 존재
- [ ] `.env.example` 존재
- [ ] `README.md` 존재 (실행 방법 포함)