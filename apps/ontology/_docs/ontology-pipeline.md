# ontology 파이프라인 전략

## 역할 정의 (Hub in Star Topology)

`apps/ontology`는 스타 토폴로지의 **허브**다.
Spoke(titanic, restaurant, silicon_valley, user)는 ontology의 포트를 통해서만 지식 그래프·벡터 컨텍스트에 접근한다. Spoke끼리 직접 참조는 아키텍처 위반.

```
          [ontology] ← Hub
         /      |      \
   [titanic] [restaurant] [silicon_valley]
                 |
              [user]
```

---

## 캐릭터 → DB 매핑

| 캐릭터 | 책임 | 인프라 |
|--------|------|--------|
| **Artanis** | 지식 그래프 — 엔티티·관계·온톨로지 | **Neo4j** |
| **Zeratul** | 컨텍스트 검색 — 임베딩·RAG | **Qdrant** |
| **Kerrigan** | 토폴로지 라우팅 — 쿼리를 Artanis/Zeratul로 분기 | (순수 도메인 로직) |

> StarCraft 캐릭터 선택 이유: Artanis(프로토스 지도자) → 지식 연결망, Zeratul(다크 템플라) → 숨겨진 맥락 탐색, Kerrigan(지휘관) → 전체 흐름 조율.

---

## 파이프라인 흐름

```
HTTP Request
    │
    ▼
KerriganTopologyRouter          ← inbound port (FastAPI)
    │
    ├─▶ ArtanisGraphUseCase     ← 질의 의도가 "관계 탐색"일 때
    │       │
    │       ▼
    │   Neo4j (Graph DB)        ← 엔티티·관계 Cypher 쿼리
    │
    └─▶ ZeratulContextUseCase   ← 질의 의도가 "유사 문서 검색"일 때
            │
            ▼
        Qdrant (Vector DB)      ← 임베딩 similarity search
            │
            ▼
    T1MidFakerOrchestrator      ← ExaOne 3.5:7.8b (core/lol/)
    (graph context + vector context → LLM prompt 조합)
            │
            ▼
        Response
```

---

## Docker 서비스 추가 계획

`docker-compose.yaml`에 아래 두 서비스를 추가한다.

```yaml
# Neo4j — Graph DB
neo4j:
  image: neo4j:5
  container_name: whoareryu-neo4j
  ports:
    - "7474:7474"   # HTTP Browser
    - "7687:7687"   # Bolt protocol
  environment:
    - NEO4J_AUTH=neo4j/changeme
  volumes:
    - neo4j_data:/data
  networks:
    - app-network

# Qdrant — Vector DB
qdrant:
  image: qdrant/qdrant:latest
  container_name: whoareryu-qdrant
  ports:
    - "6333:6333"   # REST API
    - "6334:6334"   # gRPC
  volumes:
    - qdrant_data:/qdrant/storage
  networks:
    - app-network
```

환경변수 (`.env`에 추가):
```
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

---

## 헥사고날 레이어 매핑

```
apps/ontology/
├── adapter/
│   ├── inbound/api/v1/
│   │   └── kerrigan_topology_router.py   ← HTTP 진입점, 라우팅 판단
│   └── outbound/repositories/
│       ├── artanis_graph_repository.py   ← Neo4j 드라이버 (neo4j-driver)
│       └── zeratul_context_repository.py ← Qdrant 클라이언트 (qdrant-client)
├── app/
│   ├── ports/
│   │   ├── input/
│   │   │   ├── artanis_graph_use_case.py      ← ABC (그래프 조회 포트)
│   │   │   ├── kerrigan_topology_use_case.py  ← ABC (라우팅 포트)
│   │   │   └── zeratul_context_use_case.py    ← ABC (컨텍스트 검색 포트)
│   │   └── output/
│   │       ├── artanis_graph_port.py           ← ABC (Neo4j 아웃포트)
│   │       └── zeratul_context_port.py         ← ABC (Qdrant 아웃포트)
│   └── use_cases/
│       ├── artanis_graph_interactor.py         ← Cypher 쿼리 조합 로직
│       ├── kerrigan_topology_interactor.py     ← 의도 분기 + LLM 호출 조합
│       └── zeratul_context_interactor.py       ← 임베딩 생성 + 검색 로직
└── dependencies/
    ├── artanis_graph_provider.py
    ├── kerrigan_topology_provider.py
    └── zeratul_context_provider.py
```

---

## 의존성 추가 (requirements.txt)

```
neo4j==5.28.1           # Neo4j Python Driver
qdrant-client==1.14.2   # Qdrant Python Client
```

---

## 구현 우선순위

| 순서 | 작업 | 검증 기준 |
|------|------|-----------|
| 1 | docker-compose에 neo4j, qdrant 서비스 추가 | 컨테이너 기동 + 포트 응답 확인 |
| 2 | ArtanisGraphRepository — Neo4j 연결 + 헬스체크 | `MATCH (n) RETURN count(n)` 성공 |
| 3 | ZeratulContextRepository — Qdrant 연결 + 컬렉션 생성 | `/collections` REST 응답 확인 |
| 4 | KerriganTopologyInteractor — 의도 분기 + Faker 호출 | 단위 테스트 통과 |
| 5 | `/ontology/query` 엔드포인트 E2E | HTTP 200 + LLM 응답 포함 |

---

## 트레이드오프 기록

| 결정 | 선택 | 이유 |
|------|------|------|
| Graph DB | Neo4j | Cypher 쿼리 가독성, Python 드라이버 성숙도 |
| Vector DB | Qdrant | 경량 Docker 이미지, REST+gRPC 지원, Rust 기반 성능 |
| LLM | ExaOne 3.5:7.8b (로컬 Ollama) | 완전 로컬 실행 — 외부 API 비용·레이턴시 없음 |
| 임베딩 | ExaOne generate → 별도 검토 | 추후 전용 임베딩 모델(예: bge-m3)과 비교 후 결정 |
