# Vercel · v0 배포 (cloud.whoareryu.www)

프론트 저장소: [whoareryu/cloud.whoareryu.www](https://github.com/whoareryu/cloud.whoareryu.www)  
v0 프로젝트와 Vercel은 **이 저장소 루트**(`app/`, `package.json`)를 기준으로 연결합니다.

---

## "Deployment was blocked" (빌드 전 차단)

GitHub에 **빨간 X — Vercel — Deployment was blocked** 가 뜨면, 대부분 **코드 오류가 아니라** Vercel이 커밋 작성자를 프로젝트 소유자로 인식하지 못한 경우입니다.

### 1) Vercel ↔ GitHub 재연결 (가장 효과적)

1. [Vercel Account → Authentication](https://vercel.com/account/settings/authentication)
2. **GitHub** 연결 해제 후 다시 연결 (Login Connections)
3. [프로젝트 Settings → Git](https://vercel.com/) 에서 저장소가 `cloud.whoareryu.www` 인지 확인

### 2) Git 작성자 = GitHub = Vercel 이메일

로컬에서 확인:

```bash
git config user.email
git config user.name
```

- `user.email` 이 **GitHub 계정에 등록·인증된 이메일**과 같아야 합니다.
- Vercel **Hobby** 플랜은 보통 **계정 소유자 본인 커밋**만 자동 배포됩니다.
- v0/다른 계정이 push 한 커밋은 Hobby에서 차단될 수 있습니다 → **본인 계정으로 한 번 더 push** 하세요.

### 3) 차단 해제 후 반드시 **새 커밋** push

실패한 배포만 "Redeploy" 하지 말고, 설정 수정 후 **새 커밋**을 올려야 합니다.

```bash
cd frontend
git add vercel.json .nvmrc
git commit -m "chore: Vercel Next.js 배포 설정"
git push origin main
```

### 4) Vercel 프로젝트 설정

| 항목 | 값 |
|------|-----|
| Framework Preset | Next.js |
| Root Directory | **`.`** (저장소 루트 — `frontend/` 아님) |
| Node.js Version | **20.x** |
| Build Command | `npm run build` (또는 `vercel.json` 사용) |
| Install Command | `npm install` |

**Environment Variables** (Production·Preview):

| 변수 | 예시 |
|------|------|
| `NEXT_PUBLIC_BACKEND_URL` | 공개 FastAPI URL (로컬 `127.0.0.1` 은 Vercel에서 동작 안 함) |

### 백엔드 없이 UI만 테스트 (standalone)

`NEXT_PUBLIC_BACKEND_URL` 을 **설정하지 않으면** Next.js `/api` 가 직접 응답합니다.

| 변수 | 필수 | 역할 |
|------|------|------|
| `GEMINI_API_KEY` | 채팅 테스트 시 | `/api/gourmet/chat`, `/api/gemini/chat` |
| `OPENWEATHER_API_KEY` | 날씨 위젯 | `/api/weather` |
| `OPENWEATHER_CITY` | 선택 (기본 Seoul) | 위치 거부 시 도시 |
| `STANDALONE_API` | 선택 `true` | `NEXT_PUBLIC_BACKEND_URL` 이 있어도 프록시 대신 standalone |

- **목 데이터:** 홈 피드·오늘의 한 끼 (실제 13만 건 DB 아님)
- **미지원:** 즐겨찾기·식단·로그인 DB 연동 → `NEXT_PUBLIC_BACKEND_URL` 필요

배포 후 확인: `https://your-app.vercel.app/api/gourmet/home-browse` → JSON + `"mode":"standalone"`

---

## 모노레포(com.ragwatson)와의 관계

| 저장소 | 역할 |
|--------|------|
| `cloud.whoareryu.www` | **프론트 전용** — v0 · Vercel 연동 대상 |
| `cloud.whoareryu` (부모) | `frontend` 를 **서브모듈**로 포함 |

Vercel/v0는 **www 저장소**만 보면 됩니다. 부모 저장소에 push 해도 www 의 Vercel 배포는 **서브모듈이 갱신·push 될 때**만 반영됩니다.

```bash
# 부모에서 서브모듈 포인터만 올린 경우 → www 에 실제 코드 push 필요
cd frontend
git push origin main
```

---

## 로컬 빌드 확인

```bash
cd frontend
npm install
npm run build
```

성공하면 Vercel 빌드 실패 원인은 대개 **환경 변수·백엔드 URL·Git 연동**입니다.

---

## v0 연동

- v0 대시보드에서 연결한 GitHub repo = `cloud.whoareryu.www`
- v0가 push 한 커밋 author 가 본인이 아니면 Hobby에서 blocked → 본인 커밋으로 재push 또는 Vercel Pro

[v0 프로젝트 이어하기](https://v0.app/chat/projects/prj_SLLKGDgdqPt701zP0ucxL1BPGVhE)

---

## 관련 문서

[[www/_docs/CLAUDE\|Frontend Docs]]
