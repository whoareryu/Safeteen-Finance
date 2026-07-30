---
type: spoke
app: admin
links:
  - star_craft
---

# LangChain 전략 — Elastic: 운용 효율성 향상

LangChain은 다양한 데이터 소스와의 통합을 통해 실시간으로 데이터를 처리하고 분석할 수
있어, 비즈니스 운영의 효율성을 크게 향상합니다. Elastic은 보안 분석가들을 지원하기
위해 LangChain을 활용해 AI 어시스턴트를 개발했습니다. 이 AI 어시스턴트는 보안 경고를
요약하고, 워크플로우를 제안하며, 쿼리 생성과 변환을 수행하여 보안 팀의 업무 효율성을
크게 향상합니다. 이 애플리케이션은 실시간으로 대량의 데이터를 처리하고 분석하여 보안
작업을 지원하는데, LangChain의 데이터 통합 및 처리 기능이 중요한 역할을 하고 있습니다.

## 구현 매핑

이 전략을 아래 `elastic_security_assistant` 유스케이스로 구현한다.

| 전략 요소 | 구현 |
|-----------|------|
| 실시간 대량 데이터 처리·분석 | `ElasticAlertRepository`가 매 요청마다 최신 보안 경고를 DB에서 조회 (캐시 재사용 금지, [langchain-harness.md](langchain-harness.md) 절대 규칙 3) |
| 보안 경고 요약 | `ElasticSecurityAssistantInteractor`가 조회한 경고 목록을 요약 프롬프트로 전달 |
| 워크플로우 제안 | `ElasticSecurityAssistantGeneratorClient`의 `ChatPromptTemplate`이 경고 컨텍스트를 기반으로 대응 워크플로우 후보를 생성 |
| 쿼리 생성·변환 | 동일 클라이언트의 별도 프롬프트 단계에서 자연어 질의 → 쿼리(DSL) 생성·변환을 수행 |

### 레이어 구성

```
domain/security_alert.py                                              # 보안 경고 엔티티
app/dtos/elastic_security_assistant_dto.py
app/ports/input/elastic_security_assistant_use_case.py
app/ports/output/elastic_alert_repository_port.py
app/ports/output/elastic_security_assistant_generator_port.py
app/use_cases/elastic_security_assistant_interactor.py
adapter/outbound/repository/elastic_alert_repository.py               # 최신 보안 경고 조회 (실시간)
adapter/outbound/client/elastic_security_assistant_generator_client.py # LangChain + ChatOllama (요약·워크플로우 제안·쿼리 생성)
adapter/inbound/api/schemas/elastic_security_assistant_schema.py
adapter/inbound/api/v1/elastic_security_assistant_router.py           # POST /admin/elastic/assist
dependencies/elastic_security_assistant_provider.py
```

### 환경 변수

로컬 Ollama 서버(`core/lol/t1_mid_faker_orchestrator.py`와 동일한 관례)를 사용한다.

```
OLLAMA_BASE_URL=http://localhost:11434   # 선택, 기본값 위와 동일
OLLAMA_MODEL=exaone3.5:2.4b              # 선택, 기본값 위와 동일
```
