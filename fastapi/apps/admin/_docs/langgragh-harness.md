---
type: spoke
app: admin
links:
  - architect
---

# LangGraph 작업 하네스

Claude가 이 저장소에서 LangGraph를 도입하거나 만질 때 지켜야 할 규칙이다.
[langchain-harness.md](langchain-harness.md)가 "LangChain을 어떻게 쓸지"를 다룬다면, 이 문서는
**"언제 LangChain만으로 부족해서 LangGraph(StateGraph)로 내려가야 하는지, 내려간다면 무엇을 지켜야
하는지"**를 다룬다. 막연한 소개가 아니라 도입 여부 판단 기준과, 도입 후 지켜야 할 체크리스트다.

---

## 0. 컨텍스트

- LangChain 1.0과 LangGraph 1.0은 2025-10-22에 같이 나왔고, 지금 구조는 **LangGraph가 런타임, LangChain이
  그 위의 미들웨어 중심 고수준 API**다. `create_agent`가 기존 `AgentExecutor`를 대체했고 내부적으로
  LangGraph 실행 엔진을 호출한다. "LangChain=체인, LangGraph=에이전트"라는 옛 구분은 안 맞는다 — 이미
  LangGraph 위에서 돌고 있고, **그래프를 직접 만질지 말지**의 문제다.
- 이 저장소는 `langgraph` 패키지가 설치돼 있지만([langchain-harness.md](langchain-harness.md) §0),
  아직 `StateGraph`를 직접 구성해 쓰는 곳은 없다. 현재 시멘틱 라우팅
  (`ontology/adapter/inbound/api/v1/semantic_routing_router.py` →
  `SemanticRoutingInteractor`)은 crud/qwen_rag/gemini 3개 목적지로만 분기하는 단일 홉(DAG) 구조이고,
  "gemini" 분기는 `OllamaLangchainChatbotGateway`(LangChain + ChatOllama, 사이클 없는 단발 응답)로
  처리된다. 이 문서는 이 구조에 **"reasoning이 필요한 질문"을 위한 사이클을 어디에, 어떻게 얹을지**의
  기준이다.

---

## 1. 언제 StateGraph로 내려가는가 (전제 조건)

아래 넷 중 **최소 하나**에 해당해야 도입을 검토한다. 하나도 해당 안 되면 오버엔지니어링이다 — 단일 턴
RAG QA 챗봇이면 LangGraph 없이 `create_agent`나 기존 단발 체인으로 충분하다.

1. **사이클이 필요할 때.** LCEL 체인은 본질적으로 DAG다. "검색 → 결과 부실 판정 → 쿼리 재작성 →
   재검색"처럼 조건부로 되돌아가는 구조를 체인으로 짜면 재귀 함수와 if문 지옥이 된다. Self-RAG,
   Corrective RAG 계열은 전부 사이클 전제다.
2. **내구성(durability).** 단계별 성공률 85%인 툴 콜을 10번 연속 돌리면 완주 확률이 약 20%로
   떨어진다 — 모델을 바꿔서 해결되는 문제가 아니라 체크포인팅과 재개로 푸는 문제다.
3. **Human-in-the-loop.** `interrupt()` + `Command(resume=...)` 조합(보통
   `HumanInTheLoopMiddleware` 경유)으로 승인 게이트를 그래프 중간에 박아야 할 때.
4. **멀티 에이전트 토폴로지.** Supervisor/Swarm 패턴, 에이전트 간 상태 공유, 부분 스트리밍이 필요할 때.

라우팅 분기가 3개 이상 생기거나 재시도 루프가 필요해지는 시점에 내려간다 — 그 전까지는 내려가지 않는다.

---

## 2. 이 저장소에서의 트리거 — 시멘틱 라우터의 "reasoning" 케이스

`QwenIntentClassifierGateway`가 분류하는 현재 3개 목적지(crud/qwen_rag/gemini) 중,
**"qwen_rag" 목적지가 반환한 컨텍스트가 부실할 때**가 위 §1-1(사이클)에 해당하는 이 저장소의 전형적
케이스다 (`SemanticRoutingInteractor._answer_with_ontology`).

- **현재:** `_search_ontology`가 빈 리스트를 반환하면 그 자리에서 "찾을 수 없습니다"로 즉시 종료한다.
  사이클이 없다.
- **도입 시 목표:** "검색 → 컨텍스트 평가 → (부실하면) 쿼리 재작성 → 재검색 → 생성" 사이클을
  `StateGraph`로 추가한다 — Corrective RAG 패턴.

**절대 시멘틱 라우터의 destination 분류 자체(crud/qwen_rag/gemini 판정, `QwenIntentClassifierGateway`)를
LangGraph로 대체하지 않는다.** 그건 여전히 단일 LLM 호출로 충분한 DAG 작업이다. 사이클이 필요한
지점(qwen_rag 분기의 재검색 루프) 안쪽에만 얹는다 — 라우터 자체를 그래프화하지 않는다.

---

## 3. 절대 규칙 (도입한다면)

1. **LangGraph는 새 output port 뒤에 둔다.** 인터랙터·도메인 코드가 컴파일된 `StateGraph`나
   `langgraph` 구체 클래스를 직접 참조하지 않는다 — 예: `app/ports/output/reasoning_graph_port.py`
   (ABC, `run(query, context) -> str` 형태)를 정의하고, 구체 그래프 컴파일·실행은
   `adapter/outbound/llm/*_graph_gateway.py`에서만 한다. langchain-harness.md 규칙 1과 동일한 이유다.
2. **기존 `SemanticRoutingInteractor`를 대체하지 않는다.** qwen_rag 분기 내부에서 컨텍스트가 부실할
   때만 선택적으로 그래프를 호출한다 — crud/gemini 분기는 무관하다.
3. **Checkpointer는 이미 있는 인프라(Postgres/Redis)를 재사용한다.** 이 사이클 하나를 위해 새 저장소를
   붙이지 않는다.
4. **`interrupt()`/`HumanInTheLoopMiddleware`는 실제 승인 게이트가 필요할 때만 도입한다.** 이
   저장소엔 아직 그런 요구가 없다 — §1-3은 지금 도입 사유가 아니다.
5. **노드 수는 최소로.** "검색 → 평가 → 재작성 → 재검색 → 생성" 5노드를 넘기지 않는다. 그 이상
   필요해지면 먼저 왜 필요한지를 이 문서에 추가하고 나서 코드를 짠다.
6. **재시도 루프에는 반드시 최대 횟수를 상수로 고정한다.** 종료 조건 없는 사이클은 무한 루프다.

---

## 4. 체크리스트

작업을 완료로 보고하기 전에 아래를 확인한다.

- [ ] §1의 전제 조건 4가지 중 최소 하나에 해당하는가? — 아니면 그래프 없이 기존 단발 호출로 되돌아간다.
- [ ] 사이클 종료 조건(최대 재시도 횟수)이 상수로 고정돼 있는가?
- [ ] LLM 프로바이더가 여전히 포트 뒤에 숨어 있는가? (langchain-harness.md 규칙 1)
- [ ] 그래프 컴파일이 요청마다 재사용 가능한 곳(어댑터 `__init__`)에서 한 번만 일어나는가, 아니면
      실수로 매 요청마다 다시 컴파일하고 있는가?
- [ ] `SemanticRoutingInteractor`의 crud/gemini 분기는 그대로인가? (§2 — 라우터 자체는 그래프화 대상 아님)

---

## 5. GraphRAG(Neo4j) 확장 여지 — 참고용, 현재 미채택

이 저장소는 pgvector(`plant_knowledge_search_port.py`)와 Neo4j(`sommelier_graph_port.py`)가 이미
역할 분담돼 있다 — pgvector는 대량 텍스트, Neo4j는 관계형 질의(`SemanticRoutingInteractor`의
`_GRAPH_SIGNALS` 키워드로 감지). `neo4j-graphrag`의 `VectorCypherRetriever` 같은 이중 그래프
(Lexical + Domain) 패턴은 멀티홉 질의("A가 좋아한 가게 사장이 운영하는 다른 매장")가 실제로 늘었을
때 검토 대상이지만, **지금은 도입하지 않는다** — 현재 sommelier 분기는 단순 Cypher 조회로 충분하고,
`retrieval_query` 커스터마이징이 필요할 만큼 복잡한 그래프 탐색 요구가 아직 없다.

---

## 6. 참고

- 관련 구현: [semantic_routing_interactor.py](../../ontology/app/use_cases/semantic_routing_interactor.py),
  [qwen_intent_classifier_gateway.py](../../ontology/adapter/outbound/llm/qwen_intent_classifier_gateway.py)
- [langchain-harness.md](langchain-harness.md)
- [neo4j-harness.md](neo4j-harness.md)
