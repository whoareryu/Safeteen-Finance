# CLAUDE.md — Frontend (www)

Next.js 프론트엔드 프로젝트 규약. 루트 규칙은 [../CLAUDE.md](../CLAUDE.md)를 먼저 읽는다.

---

## 스택

| 항목 | 값 |
|------|-----|
| 프레임워크 | Next.js 16 (App Router) |
| 언어 | TypeScript 5.7 (strict) |
| 스타일 | Tailwind CSS v4 |
| UI 컴포넌트 | shadcn/ui (Radix UI 기반) |
| 폼 | react-hook-form + zod |
| 아이콘 | lucide-react |
| 차트 | recharts |
| 패키지 매니저 | pnpm |
| 진입점 | `app/layout.tsx`, `app/page.tsx` |
| 백엔드 연결 | `BACKEND_URL=http://backend:8000` (Docker 내부) |

---

## 디렉터리 구조

```text
www/
├── app/                        # App Router 페이지·레이아웃
│   ├── layout.tsx
│   ├── page.tsx
│   ├── api/                    # Next.js Route Handlers (백엔드 프록시)
│   ├── food/
│   ├── mypage/
│   ├── portfolio/
│   ├── restaurants/
│   ├── stores/
│   └── topics/
├── components/                 # 공유 컴포넌트 (shadcn 포함)
├── hooks/                      # 커스텀 훅
├── lib/                        # 유틸·API 클라이언트
├── public/                     # 정적 파일
└── styles/                     # 글로벌 CSS
```

---

## 규약

### 컴포넌트

- shadcn/ui 컴포넌트는 `components/ui/`에 위치. 직접 수정하지 않는다.
- 비즈니스 컴포넌트는 `components/` 하위 도메인 폴더로 구분한다.
- Server Component를 기본으로 한다. 클라이언트 상태가 필요할 때만 `"use client"` 추가.

### API 통신

- 백엔드 직접 호출은 `app/api/` Route Handler를 경유한다 (CORS·인증 처리).
- `lib/` 에 fetch 래퍼·타입 정의를 두고, 컴포넌트에서 직접 `fetch`를 쓰지 않는다.

### 타입

- API 응답 타입은 백엔드 Pydantic 스키마와 대응하도록 `lib/types/` 에 정의한다.
- `any` 사용 금지. 불명확하면 `unknown` 후 타입 가드를 쓴다.

### 폼

- 모든 폼은 `react-hook-form` + `zod` 스키마 검증.
- 서버 액션보다 Route Handler + `fetch`를 우선한다 (백엔드와 분리 유지).

### 스타일

- Tailwind 유틸리티 클래스만 사용. 인라인 `style` 속성 금지.
- `cn()` (`lib/utils.ts`) 으로 조건부 클래스 병합.
- 다크모드: `next-themes` — `dark:` variant로 처리.

---

## 실행

```powershell
cd www
pnpm dev          # 개발 서버 http://localhost:3000
pnpm build        # 프로덕션 빌드
pnpm lint         # ESLint
```

Docker:
```powershell
# 루트에서
docker-compose up frontend
```

---

## 개발 백로그

- [ ] `lib/` API 클라이언트 타입 정의 정비
- [ ] Route Handler 백엔드 프록시 패턴 통일
- [ ] 공통 에러 바운더리·로딩 UI 컴포넌트 작성

---

## 관련 문서

[[CLAUDE\|Root]] · [[REACT_RULES]] · [[VERCEL_V0_DEPLOY]]
