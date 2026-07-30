---
paths:
  - "fastapi/apps/**/*.py"
---

# API 규칙 (fastapi)

`fastapi/apps/admin/`(langchain 챗 기능)·`fastapi/apps/ontology/`(시멘틱 라우팅
기능)에서 실제로 쓰이는 패턴을 기준으로 한다. 레이어 배치는 `fastapi/CLAUDE.md`
"헥사고날 아키텍처 — feature 슬라이스"를 따른다.

---

## 1. 요청/응답 스키마 — 얇은 Pydantic 모델

`adapter/inbound/api/schemas/{feature}_schema.py`에 둔다. 필드는 검증 로직 없이
평평하게 선언한다 — 검증·가공은 유스케이스/도메인 레이어의 책임이다.

```python
# apps/admin/adapter/inbound/api/schemas/langchain_chat_schema.py
from pydantic import BaseModel

class ChatRequestSchema(BaseModel):
    message: str

class ChatResponseSchema(BaseModel):
    reply: str
```

`Field(default_factory=...)`는 리스트 기본값에만 쓴다.

```python
# apps/ontology/adapter/inbound/api/schemas/semantic_routing_schema.py
class SemanticRoutingResponse(BaseModel):
    answer: str
    destination: str
    entities: list[str] = Field(default_factory=list)
```

---

## 2. DTO는 `@dataclass(frozen=True)`

유스케이스 입출력은 Pydantic이 아니라 불변 dataclass로 도메인 레이어에 둔다
(`app/dtos/{feature}_dto.py`). Command(입력)/Result(출력)로 이름 짓는다.

```python
# apps/admin/app/dtos/langchain_chat_dto.py
@dataclass(frozen=True)
class ChatCommand:
    message: str

@dataclass(frozen=True)
class ChatResult:
    reply: str
```

---

## 3. 라우터 — 매핑은 mapper로, 로직은 유스케이스로

라우터(`adapter/inbound/api/v1/{feature}_router.py`)는 요청 스키마를 DTO로
바꿔 유스케이스를 호출하고, 결과를 mapper로 응답 스키마로 바꾸는 것 외엔 아무
것도 하지 않는다.

```python
# apps/admin/adapter/inbound/api/v1/langchain_chat_router.py
langchain_chat_router = APIRouter(prefix="/langchain", tags=["langchain-chat"])

@langchain_chat_router.post("/chat", summary="LangChain 어시스턴트와 대화")
async def chat(
    body: ChatRequestSchema,
    use_case: LangchainChatUseCase = Depends(get_langchain_chat_use_case),
) -> ChatResponseSchema:
    result = await use_case.chat(ChatCommand(message=body.message))
    return to_response(result)
```

```python
# apps/admin/adapter/inbound/mappers/langchain_chat_mapper.py
def to_response(result: ChatResult) -> ChatResponseSchema:
    return ChatResponseSchema(reply=result.reply)
```

- `prefix`는 라우터 파일마다 하나의 feature를 대표하는 짧은 세그먼트.
- 최종 URL은 `main.py`에서 `app.include_router(xxx_router, prefix="/api")`로
  조립되므로, 라우터 자체 prefix에 `/api`를 중복해서 넣지 않는다.

---

## 4. 에러 처리 — `HTTPException` + 한국어 `detail`

```python
# apps/ontology/adapter/inbound/api/v1/pose_router.py
raise HTTPException(status_code=400, detail=f"지원하지 않는 Content-Type입니다: {file.content_type}")
raise HTTPException(status_code=413, detail="파일 크기가 10MB를 초과했습니다.")
raise HTTPException(status_code=400, detail="person_boxes 형식이 올바르지 않습니다.") from e
```

- `detail`은 사용자에게 그대로 노출될 수 있으므로 한국어로, 내부 스택트레이스나
  시크릿을 담지 않는다.
- 원인 예외를 삼키지 않는다 — `raise ... from e`.

---

## 5. 의존성 주입 — `Depends(get_{feature}_use_case)`만

라우터·유스케이스에서 구현체(어댑터)를 직접 import하지 않는다. 조합은
`dependencies/{feature}_provider.py`의 `get_{feature}_use_case()`에서만 한다
(DIP). `Depends`는 중첩 가능 — 상위 provider가 하위 provider를 `Depends`로
받으면 FastAPI가 체인을 알아서 해석한다.

```python
# apps/admin/dependencies/langchain_chat_provider.py
def get_langchain_chat_use_case(
    semantic_routing: SemanticRoutingUseCase = Depends(get_semantic_routing_use_case),
) -> LangchainChatUseCase:
    return LangchainChatInteractor(generator=OntologySemanticRoutingChatClient(semantic_routing))
```

---

## 6. 스포크는 허브 포트만 참조

`admin`(spoke)이 `ontology`(hub)를 쓸 때도 hub의 포트/유스케이스 인터페이스만
import한다 — hub 내부 구현체를 직접 조립하지 않는다. 스포크→스포크 직접 임포트는
`lint-imports`가 정적으로 차단한다. 상세는 `fastapi/CLAUDE.md` "스타 토폴로지" 참고.
