---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangChain 전략 — NCL: 최적화된 여행 계획 제공

LangChain은 사용자 맞춤형 프롬프팅 및 파인튜닝 기능을 통해 특정 산업의 요구에 맞춘
솔루션을 제공합니다. NCL(노르웨이 크루즈 라인)은 LangChain을 이용해 고객들이 이상적인
크루즈 여행을 계획할 수 있도록 돕는 AI 어시스턴트를 개발했습니다. 이 시스템은 고객의
선호도와 탐색 기록을 기반으로 맞춤형 추천을 제공하며, LangChain을 통해 실시간으로
변화하는 고객 요구에 대응할 수 있습니다.

## 구현 매핑

이 전략을 아래 `ncl_trip_planner` 유스케이스로 구현한다.

| 전략 요소 | 구현 |
|-----------|------|
| 고객 선호도·탐색 기록 기반 맞춤 추천 | `NclPreferenceRepository`가 고객의 탐색 이력·선호도를 조회해 컨텍스트로 제공 |
| 실시간 고객 요구 대응 | `NclPreferenceRepository`가 매 요청마다 최신 탐색 기록을 DB에서 조회 (요청 시점 이전 캐시 재사용 금지, [langchain-harness.md](langchain-harness.md) 절대 규칙 3) |
| 맞춤형 프롬프팅 | `NclTripPlannerGeneratorClient`의 `ChatPromptTemplate`이 선호도 + 탐색 이력 + 사용자 질문을 결합 |
| 산업 특화 AI 어시스턴트 | `NclTripPlannerInteractor` — 선호도 조회 → LangChain 체인(`prompt \| llm \| parser`) 호출 → 맞춤 여행 추천 반환 |

### 레이어 구성

```
domain/traveler_preference.py                                    # 고객 선호도·탐색 이력 엔티티
app/dtos/ncl_trip_planner_dto.py
app/ports/input/ncl_trip_planner_use_case.py
app/ports/output/ncl_preference_repository_port.py
app/ports/output/ncl_trip_planner_generator_port.py
app/use_cases/ncl_trip_planner_interactor.py
adapter/outbound/repository/ncl_preference_repository.py         # 탐색 이력 조회 (실시간)
adapter/outbound/client/ncl_trip_planner_generator_client.py     # LangChain + ChatOllama
adapter/inbound/api/schemas/ncl_trip_planner_schema.py
adapter/inbound/api/v1/ncl_trip_planner_router.py                # POST /admin/ncl/trip-plan
dependencies/ncl_trip_planner_provider.py
```

### 환경 변수

로컬 Ollama 서버(`core/lol/t1_mid_faker_orchestrator.py`와 동일한 관례)를 사용한다.

```
OLLAMA_BASE_URL=http://localhost:11434   # 선택, 기본값 위와 동일
OLLAMA_MODEL=exaone3.5:2.4b              # 선택, 기본값 위와 동일
```
