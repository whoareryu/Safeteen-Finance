---
type: spoke
app: admin
links:
  - architect
---

# LangGraph + Neo4j 확장 전략 — 로드맵 (아직 미착수)

이 문서는 **로드맵**이다. [langgragh-harness.md](langgragh-harness.md)가 "언제 LangGraph로
내려가야 하는가"의 판단 기준(§1)과 도입 시 절대 규칙(§3)을 다룬다면, 이 문서는
**"내려가기로 결정했을 때 어떤 순서로 진행하는가"**를 다룬다.

**착수 조건이 아직 충족되지 않았다.** langgragh-harness.md §1(사이클/내구성/HITL/멀티에이전트)
중 최소 하나에 해당해야 하고, §5는 GraphRAG 확장을 "멀티홉 질의가 실제로 늘었을 때"로 보류해뒀다.
이 문서는 그 조건이 충족되는 시점에 참고할 실행 순서이지, 지금 바로 시작하라는 신호가 아니다.
**코드는 아직 한 줄도 쓰지 않는다.**

---

## 0. 두 가지를 나눠서 생각한다

이 확장은 서로 다른 두 가지 변화가 섞여 있다 — 하나로 묶어서 생각하면 헷갈린다.

1. **"LangChain → LangGraph"는 오케스트레이션 방식의 변화다.** 체인(DAG, 정해진 순서)에서
   그래프(노드+조건부 엣지)로 바뀐다. langgragh-harness.md §1의 판단 기준과 동일한 문제다.
2. **"pgvector → +Neo4j"는 저장소를 하나 더 추가하는 것이지, 기존 걸 버리는 게 아니다.**
   이 저장소는 이미 역할이 나뉘어 있다(langgragh-harness.md §5):
   - pgvector(`ontology/app/ports/output/plant_knowledge_search_port.py`) — 유사도 검색, 대량 텍스트
   - Neo4j(`ontology/app/ports/output/sommelier_graph_port.py`) — 관계 탐색("이 식당 → 이 셰프 →
     다른 식당" 류의 멀티홉 질의)

   즉 **둘 다 필요하고 역할이 다르다.** 이 로드맵은 pgvector를 없애는 게 아니라, "언제는 pgvector,
   언제는 Neo4j"를 지금처럼 `SemanticRoutingInteractor`의 키워드 신호(`_GRAPH_SIGNALS`)가 아니라
   **LangGraph가 판단하게 만드는** 확장이다.

---

## 1. 로드맵 (7단계)

**1단계 — Neo4j 스키마 설계 (코드 없이, 종이/그림으로 먼저)**
- 노드(Node) 후보: `Restaurant`, `User`, `Cuisine`, `Chef`
- 관계(Relationship) 후보: `(User)-[:LIKED]->(Restaurant)`, `(Restaurant)-[:SERVES]->(Cuisine)`
- 그래프 DB는 그림으로 먼저 설계하는 편이 압도적으로 쉽다.

**2단계 — Neo4j를 "독립적으로" 먼저 연결**
- LangGraph 없이 `neo4j` 드라이버로 쿼리 몇 개를 직접 날려본다.
- Cypher 기본 문법 연습. 이 저장소엔 이미 `sommelier_graph_repository.py`(순수 Cypher, APOC/GDS
  플러그인 불필요, neo4j-strategy.md §2)가 있으니 그 스타일을 참고한다.
- 이 단계에서 LangGraph는 아직 건드리지 않는다.

**3단계 — LangGraph로 최소 그래프 하나 만들기**
- 노드 2개짜리 최소 그래프부터: `START → 의도분류 노드 → END`.
- 조건부 엣지(conditional edge) 하나 추가: "맛집 검색 의도면 A로, 일반 대화면 B로".
- langgragh-harness.md §3-5 "노드 수는 최소로" 규칙을 여기서부터 지킨다 — 전체 그래프가
  5노드(검색→평가→재작성→재검색→생성)를 넘지 않도록 설계한다.

**4단계 — 기존 pgvector 로직을 LangGraph 노드로 이식**
- 새로 짜는 게 아니라, 지금 있는 유사도 검색 코드(`plant_knowledge_search_port.py` 구현체)를
  노드 함수 하나로 감싼다.

**5단계 — Neo4j 검색을 또 다른 노드로 추가**
- "관계 기반 추천"을 담당하는 노드를 새로 작성한다.
- 이 시점의 그래프 형태:
  ```
  START → 의도분류 → (조건) → pgvector 노드 or Neo4j 노드 → 결과합성 → END
  ```

**6단계 — 두 결과를 합치는 노드 추가**
- 상황에 따라 pgvector 결과 + Neo4j 결과를 둘 다 써야 할 수도 있다.
- "종합 답변 생성" 노드에서 두 소스를 합쳐 LLM에 전달한다.

**7단계 — State 관리 이해**
- LangGraph의 핵심은 `State` — 그래프를 흐르는 동안 누적되는 데이터.
- 예: `{"query": ..., "pgvector_results": [...], "neo4j_results": [...], "final_answer": ...}`
- 각 노드는 State를 읽고, 수정하고, 다음 노드로 넘긴다.

---

## 2. 기존 인프라와의 연결

- FastAPI 백엔드는 그대로 유지한다. LangGraph 그래프는 langgragh-harness.md §3-1 규칙대로
  **output port 뒤의 어댑터 하나**로 호출한다 — 인터랙터가 컴파일된 `StateGraph`를 직접 참조하지 않는다.
- Neo4j는 이미 `cloud.whoareryu` Docker 스택에 배선돼 있다(neo4j-strategy.md §1-2) — 컨테이너·연결
  설정을 재사용한다. 새 인프라를 추가하지 않는다.
- "라우팅 로직은 백엔드 내부에 숨긴다" 원칙을 그대로 적용한다 — 프론트(`www`)는 그래프 구조를 몰라도 된다.

---

## 3. 착수 전 체크리스트

이 로드맵을 실제로 시작하기 전에 확인한다.

- [ ] langgragh-harness.md §1의 전제 조건(사이클/내구성/HITL/멀티에이전트) 중 최소 하나에 해당하는가?
- [ ] langgragh-harness.md §5의 보류 조건("멀티홉 질의가 실제로 늘었을 때")이 실제로 관측됐는가?
- [ ] 1단계(스키마 설계)를 코드 없이 먼저 끝냈는가?
- [ ] 최종 그래프가 5노드를 넘지 않는가? (§1-3단계 참고)
- [ ] 재시도/재검색 루프에 최대 횟수가 상수로 고정될 계획인가? (무한 루프 방지)

---

## 4. 참고

- [langgragh-harness.md](langgragh-harness.md) — 도입 판단 기준·절대 규칙
- [neo4j-strategy.md](neo4j-strategy.md) — 현재 Neo4j Docker 배포 구성
- [neo4j-harness.md](neo4j-harness.md) — 그래프 데이터 모델(노드/라벨/관계/속성) 기초
- 관련 기존 구현: [semantic_routing_interactor.py](../../ontology/app/use_cases/semantic_routing_interactor.py),
  [sommelier_graph_repository.py](../../ontology/adapter/outbound/repositories/sommelier_graph_repository.py),
  [plant_knowledge_search_port.py](../../ontology/app/ports/output/plant_knowledge_search_port.py)
