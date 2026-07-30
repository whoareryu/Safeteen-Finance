---
name: deploy
description: |
  이 저장소의 백엔드(Docker + Cloudflare Tunnel)를 배포합니다.
  프론트엔드(www)는 Vercel이 별도로 배포하므로 이 스킬의 대상이 아니다.
argument-hint: "[backend|status]"
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
model: sonnet
---

## 배포 대상

- **프론트엔드(`www/`)**: Vercel이 담당한다 (`whoareryu.cloud`/`www.whoareryu.cloud`
  → Vercel CNAME). 이 스킬은 건드리지 않는다.
- **백엔드(`fastapi/`)**: Docker 호스트에서 `fastapi/docker-compose.yaml`로 기동되고,
  Cloudflare Tunnel(named tunnel `whoareryu.cloud`)로 노출된다. 이 스킬이 다룬다.

## 배포 절차 (`fastapi/start.sh`)

```bash
cd fastapi && ./start.sh
```

내부적으로 아래를 순서대로 수행한다.

1. `docker compose --env-file .env -f docker-compose.yaml pull`
   — 미리 빌드된 이미지를 레지스트리에서 받는다 (로컬 코드를 그 자리에서 빌드하지
   않는다 — 이미지 빌드/푸시가 선행돼야 반영된다).
2. `docker compose ... up -d` — `backend`/`auth`/`n8n`/`pgvector`/`redis`/`neo4j`/
   `cloudflared`/`adminer` 컨테이너 기동.
3. `docker image prune -f` — 안 쓰는 이전 이미지 정리.
4. `./start-tunnel.sh` (fastapi/ 안) — Gmail 웹훅 전용 별도 quick tunnel (메인 API 터널과 무관).

## 배포 전 체크리스트

- [ ] `fastapi`: `python -m pytest` 통과
- [ ] `www`: `pnpm build` 통과 (배포는 Vercel이 별도로 하지만, 백엔드 API 계약을
      바꿨다면 프론트도 같이 빌드 확인)
- [ ] `.env*` 변경분이 있다면 `.env.example`도 같이 갱신했는지 (실제 값은 커밋하지 않는다)
- [ ] `auth`/`backend`가 같은 이미지·다른 엔트리포인트라는 점 — `auth_main.py` 쪽
      변경이 `main.py` 쪽에 의도치 않게 영향을 주지 않는지

## 상태 확인

```bash
docker compose -f fastapi/docker-compose.yaml ps
docker compose -f fastapi/docker-compose.yaml logs -f backend
docker compose -f fastapi/docker-compose.yaml logs -f auth
```

Cloudflare Tunnel 상태(터널 자체가 살아있는지 vs 컨테이너만 죽었는지 구분)는
Cloudflare 대시보드 **Zero Trust → Networks → Tunnels**에서 `Healthy`/`Down`으로
확인한다 — `docker compose ps`만으로는 터널 연결 상태를 알 수 없다.
