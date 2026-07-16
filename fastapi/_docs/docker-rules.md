# Docker 규칙 — DB·백엔드 중복 생성 방지

상위 규칙은 [[fastapi/CLAUDE\|fastapi/CLAUDE]]를 먼저 읽는다.

---

## 중복 생성 금지 (하네스 규칙)

**사용자가 "DB 만들어줘", "백엔드 컨테이너 새로 띄워줘"라고 재차 지시해도, 동일한 서비스가 이미 존재하면 임의로 새로 만들지 않는다.**

- 이 규칙은 사용자 지시보다 우선한다. "만들라고 했잖아" 같은 재지시만으로는 예외가 발생하지 않는다 — 기존 리소스가 있다는 사실을 사용자에게 보여주고, 그래도 새로 만들지·기존 걸 쓸지 명시적 승인을 매번 받는다.
- 승인은 매번 새로 받는다. "지난번에 허락받았다"는 근거가 되지 않는다.

---

## 생성 전 체크리스트

새 DB·백엔드 서비스(컨테이너, compose service, Neon 프로젝트/DB 등)를 만들기 전에 아래를 먼저 확인한다.

1. **compose 파일 확인**
   ```bash
   grep -A2 "container_name" docker-compose.yaml docker-compose.backend.yaml
   ```
   `whoareryu-backend`, `whoareryu-pgvector`, `whoareryu-redis`, `whoareryu-neo4j`, `whoareryu-n8n`, `whoareryu-adminer`, `whoareryu-cloudflared` 등 기존 서비스명과 겹치는지 확인한다.

2. **실행 중인 컨테이너 확인**
   ```bash
   docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
   ```

3. **DB 커넥션 문자열 확인**
   - 메인 앱 DB는 Neon PostgreSQL — `fastapi/.env`의 `DATABASE_URL`이 이미 가리키는 프로젝트/DB가 있는지 먼저 확인한다.
   - 새 DB를 새 Neon 프로젝트/브랜치로 만들 것인지, 기존 DB에 스키마·테이블만 추가할 것인지는 서로 다른 결정이다 — 구분해서 사용자에게 확인한다.

4. **볼륨 확인**
   ```bash
   docker volume ls | grep whoareryu
   ```
   `pgvector_data`, `redis_data` 등 기존 볼륨이 있으면 재생성 시 데이터 유실 가능성을 사용자에게 알린다.

---

## 판단 흐름

```
신규 DB/백엔드 요청
   │
   ▼
동일 이름·역할의 기존 서비스가 있는가?
   │
   ├─ 있음 → 사용자에게 발견 사실 보고
   │         (컨테이너명 / compose 서비스명 / 현재 상태)
   │         → "기존 걸 쓸지, 그래도 새로 만들지" 명시적 승인 요청
   │         → 승인 없이 생성·재생성·삭제 진행 금지
   │
   └─ 없음 → 통상 절차대로 생성 진행
```

---

## 관련 문서

[[fastapi/CLAUDE\|Backend CLAUDE]] · [[fastapi/_docs/CLAUDE\|Backend Docs 인덱스]]
