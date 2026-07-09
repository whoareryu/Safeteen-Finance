# CLAUDE.md — Frontend (www)

Next.js 프론트엔드 프로젝트 규약. 루트 규칙은 [../CLAUDE.md](../CLAUDE.md)를 먼저 읽는다.

---

## 스택

| 항목 | 값 |
|------|-----|
| 프레임워크 | Next.js 16.2.6 (App Router) |
| 언어 | TypeScript 5.7.3 (strict) |
| 스타일 | Tailwind CSS v4 |
| UI 컴포넌트 | shadcn/ui (Radix UI 기반) |
| 폼 | react-hook-form + zod |
| 아이콘 | lucide-react |
| 차트 | recharts |
| 패키지 매니저 | npm (package-lock.json) |
| 진입점 | `app/layout.tsx`, `app/page.tsx` |
| 백엔드 프록시 | `next.config.mjs` rewrites → `NEXT_PUBLIC_BACKEND_URL` (Docker: `http://backend:8000`) |

---

## 디렉터리 구조

```text
www/
├── app/                        # App Router 페이지·레이아웃
│   ├── layout.tsx
│   ├── page.tsx
│   ├── api/                    # Next.js Route Handlers
│   │   ├── auth/               # 로그인·회원가입 프록시
│   │   ├── chat/               # Gemini 채팅
│   │   ├── gemini/
│   │   ├── gourmet/            # 맛집 API 프록시
│   │   ├── login/
│   │   ├── signup/
│   │   ├── titanic/            # Titanic 분석 API 프록시
│   │   └── weather/
│   ├── food/                   # 카테고리별 맛집 브라우즈
│   ├── mypage/                 # 마이페이지 (즐겨찾기·식비계획)
│   ├── portfolio/              # 포트폴리오 (titanic 앱 포함)
│   ├── restaurants/            # 식당 상세
│   ├── stores/                 # 매장 목록
│   └── topics/                 # 주제별 맛집
├── components/                 # 공유 컴포넌트
│   ├── ui/                     # shadcn/ui 자동생성 — 직접 수정 금지
│   └── *.tsx                   # 비즈니스 컴포넌트
├── lib/                        # API 클라이언트·유틸·타입
│   ├── auth.ts
│   ├── backend-proxy.ts
│   ├── favorites.ts
│   ├── gourmet.ts
│   ├── gourmet-topics.ts
│   ├── navigation.ts
│   └── utils.ts                # cn() 등 공통 유틸
├── hooks/                      # 커스텀 훅
├── public/                     # 정적 파일
└── next.config.mjs             # rewrites (백엔드 프록시 경로 정의)
```

---

## API 프록시 구조

백엔드 직접 호출은 `next.config.mjs`의 `rewrites`로 처리한다.  
브라우저 → Next.js `/api/*` → `NEXT_PUBLIC_BACKEND_URL` (백엔드 컨테이너).

```js
// next.config.mjs
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
// Docker 내부: NEXT_PUBLIC_BACKEND_URL=http://backend:8000
// 로컬 개발:   NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000 (.env.local)
```

현재 등록된 rewrite 경로:

| 프론트 경로 | 백엔드 경로 |
|------------|------------|
| `/api/titanic/walter/myself` | `{NEXT_PUBLIC_BACKEND_URL}/api/titanic/walter/myself` |
| `/api/titanic/chat` | `{NEXT_PUBLIC_BACKEND_URL}/api/titanic/chat` |
| `/api/titanic/upload` | `{NEXT_PUBLIC_BACKEND_URL}/api/titanic/upload` |
| `/api/titanic/james/upload` | `{NEXT_PUBLIC_BACKEND_URL}/api/titanic/james/upload` |
| `/api/gourmet/:path*` | `{NEXT_PUBLIC_BACKEND_URL}/gourmet/:path*` |
| `/api/chat` | `{NEXT_PUBLIC_BACKEND_URL}/chat` |
| `/api/auth/:path*` | `{NEXT_PUBLIC_BACKEND_URL}/auth/:path*` |
| `/api/weather` | `{NEXT_PUBLIC_BACKEND_URL}/weather` |

새 백엔드 엔드포인트 추가 시 반드시 `next.config.mjs` rewrites에 등록.

---

## 규약

### 컴포넌트

- `components/ui/` — shadcn/ui 자동생성. **직접 수정 금지**.
- 비즈니스 컴포넌트는 `components/` 바로 아래 도메인별 파일.
- **Server Component 기본**. 클라이언트 상태·이벤트 핸들러가 필요할 때만 `"use client"`.

### API 통신

- 컴포넌트에서 `fetch` 직접 호출 금지. `lib/` 래퍼를 경유한다.
- Route Handler(`app/api/`)는 인증 헤더 주입·CORS 처리 용도.
- `X-User-Id` 헤더로 인증된 사용자 ID를 백엔드에 전달한다.

### 타입

- API 응답 타입은 `lib/types/` (또는 각 `lib/*.ts`)에 백엔드 스키마와 대응하도록 정의.
- `any` 사용 금지. 불명확하면 `unknown` + 타입 가드.

### 폼

- 모든 폼은 `react-hook-form` + `zod` 스키마 검증.
- 서버 액션보다 Route Handler + `fetch` 우선 (백엔드와 분리 유지).

### 스타일

- Tailwind 유틸리티 클래스만 사용. 인라인 `style` 속성 금지.
- 조건부 클래스 병합은 `cn()` (`lib/utils.ts`).
- 다크모드: `next-themes` — `dark:` variant.

---

## 실행

```bash
# 로컬 개발
cd www
npm run dev        # http://localhost:3000

# 빌드
npm run build
npm run start

# Docker (프로젝트 루트에서)
docker compose up --build
```

환경변수 (`www/.env.local`):
```
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000   # 로컬
# Docker 실행 시 docker-compose.yaml의 environment가 오버라이드
# NEXT_PUBLIC_BACKEND_URL=http://backend:8000
```

---

## 주요 리다이렉트

`next.config.mjs`에 등록된 레거시 경로 → 현재 경로:

| 레거시 | 현재 |
|--------|------|
| `/titanic` | `/portfolio/titanic` |
| `/seoulmate` | `/portfolio` |
| `/history` | `/` |
| `/nature` | `/food/hansik` |

---

## 알려진 이슈 / 백로그

| 항목 | 상태 |
|------|------|
| `lib/` API 클라이언트 타입 정의 정비 | 진행 중 |
| Route Handler 백엔드 프록시 패턴 통일 | 진행 중 |
| 공통 에러 바운더리·로딩 UI | 미구현 |
| `X-User-Id` 기반 인증 → JWT 전환 | 운영 전 필요 |

---

## 관련 문서

[[www/_docs/CLAUDE\|Frontend Docs]]