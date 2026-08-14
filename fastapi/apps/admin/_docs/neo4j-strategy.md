---
type: spoke
app: admin
links:
  - architect
---

# Neo4j 전략 — Docker 배포

[langgragh-harness.md](langgragh-harness.md) §5(GraphRAG 확장 여지)가 전제하는 인프라를 문서화한다.
Neo4j는 이미 이 저장소의 Docker 스택에 설치·배선되어 sommelier 그래프 조회에 쓰이고 있다 — 이 문서는
"어떻게 설치할까"가 아니라 **지금 어떻게 돌아가고 있고, GraphRAG를 실제로 얹을 때 뭘 먼저 확인해야
하는지**를 정리한다.

---

## 1. 현재 배포 구성

로컬 실행은 더 이상 지원하지 않고, `fastapi/docker-compose.yaml` 하나로 통합돼 클라우드
호스트(EC2)에서만 기동한다. `neo4j` 서비스도 이 파일 하나에만 정의돼 있다.

```yaml
neo4j:
  image: neo4j:5
  container_name: whoareryu-neo4j
  ports:
    - "7474:7474"   # HTTP — Neo4j Browser
    - "7687:7687"   # Bolt — 드라이버 프로토콜
  environment:
    - NEO4J_AUTH=${NEO4J_USER:-neo4j}/${NEO4J_PASSWORD:-changeme}
  volumes:
    - neo4j_data:/data
  networks:
    - app-network
```

`backend`(및 `auth`는 아님, `backend`만) 서비스가 `depends_on: neo4j`로 시작 순서를 보장하고,
`NEO4J_URI=bolt://neo4j:7687`로 같은 `app-network` 브리지 안에서 컨테이너 이름으로 접속한다.

---

## 2. 연결 관례

애플리케이션 코드는 driver를 직접 만들지 않는다 — 다른 인프라 클라이언트와 동일하게
`core.infra.secret_manager`를 거친다.

```python
# apps/ontology/dependencies/sommelier_graph_provider.py
uri=secret_manager.get_secret("NEO4J_URI", "bolt://neo4j:7687"),
user=secret_manager.get_secret("NEO4J_USER", "neo4j"),
password=secret_manager.get_secret("NEO4J_PASSWORD", "changeme"),
```

`SommelierRepository`(`apps/ontology/adapter/outbound/repositories/sommelier_graph_repository.py`)가
`neo4j` 파이썬 드라이버(`AsyncGraphDatabase`)로 순수 Cypher만 실행한다 — APOC·GDS 등 플러그인
의존성은 없다.

로컬(비Docker) 실행 시 `fastapi/.env`에 아래 3개를 채운다 (`.env.example` 참고):

```
NEO4J_URI=bolt://localhost:7687   # 컨테이너 밖에서 접속할 땐 neo4j 대신 localhost
NEO4J_USER=neo4j
NEO4J_PASSWORD=<실제 비밀번호>
```

---

## 3. 운영 체크리스트

- [ ] **기본 비밀번호 방치 금지.** `NEO4J_PASSWORD`를 `.env`에 설정 안 하면 `changeme`로 조용히
      폴백한다. 반드시 실제 비밀번호를 `fastapi/.env`에 채워야 한다 — placeholder를 그대로 쓴 채
      올라가지 않았는지 확인.
- [ ] **`fastapi/docker-compose.yaml`은 `.env`를 암묵적으로 안 읽는다.** 파일 상단 주석대로
      `docker compose --env-file fastapi/.env -f fastapi/docker-compose.yaml up`처럼 `--env-file`을
      명시해야 `${NEO4J_USER}`/`${NEO4J_PASSWORD}` 치환이 실제로 적용된다. 빠뜨리면 위 `changeme`
      폴백으로 조용히 넘어간다.
- [ ] **`neo4j_data` 볼륨이 실제로 영속되는지.** `restart: unless-stopped`가 있어도 `docker compose
      down -v`를 실수로 쓰면 그래프 데이터가 통째로 날아간다 — `-v` 없이 `down`을 쓰는지 항상 확인.
- [ ] **헬스체크가 없다.** `backend`가 `depends_on: neo4j`로 시작 순서만 보장할 뿐, Neo4j가 완전히
      기동됐는지는 확인하지 않는다. 콜드 스타트 시 `sommelier_graph_router` 첫 요청이 연결 실패로
      튈 수 있다 — 재현되면 `depends_on`에 `condition: service_healthy` + Neo4j `healthcheck`
      추가를 검토한다.

---

## 4. LangGraph 하네스와의 연결 지점 — GraphRAG 채택 시 확인할 것

[langgragh-harness.md](langgragh-harness.md) §5는 `VectorCypherRetriever` 같은 GraphRAG 패턴을
"멀티홉 질의가 실제로 늘었을 때" 검토 대상으로 보류해뒀다. 실제로 채택하게 되면 이 인프라 쪽에서
먼저 확인할 것:

1. **버전.** 이미지 태그가 `neo4j:5`(구 semantic 버전 라인)로 고정돼 있다. 하네스 문서가 언급한
   "필터 걸린 벡터 검색이 인덱스 내부 필터링으로 자동 라우팅되는" 최적화는 Neo4j가 calendar
   versioning(예: `2026.01`)으로 넘어간 이후 라인에서 들어간 개선이다 — 지역·가격대 필터를 자주
   거는 워크로드로 GraphRAG를 붙일 계획이면, 그 시점에 실제 사용 가능한 태그를 확인하고 `neo4j:5`를
   유지할지 올릴지부터 결정한다. 별다른 조사 없이 5.x에 남아 있어도 벡터 인덱스 자체(네이티브,
   플러그인 불필요)는 5.11+부터 지원되므로 `VectorRetriever`/`VectorCypherRetriever` 기본 동작은
   가능하다 — 위 최적화만 없을 뿐이다.
2. **볼륨 사이징.** 지금 `neo4j_data`는 sommelier 그래프(적은 개체 수, 얕은 관계) 정도만 담고
   있다. GraphRAG로 청크(Chunk) 노드까지 적재하면 데이터 볼륨이 커진다 — 디스크 여유를 미리
   확인한다.
3. **플러그인은 여전히 불필요.** `neo4j-graphrag` 패키지의 리트리버들은 네이티브 벡터 인덱스와
   순수 Cypher만으로 동작한다 — APOC/GDS 플러그인을 compose에 추가할 필요는 없다.

---

## 5. 참고

- [langgragh-harness.md](langgragh-harness.md)
- [neo4j-harness.md](neo4j-harness.md)
- 실제 배선: [sommelier_graph_provider.py](../../ontology/dependencies/sommelier_graph_provider.py),
  [sommelier_graph_repository.py](../../ontology/adapter/outbound/repositories/sommelier_graph_repository.py)
