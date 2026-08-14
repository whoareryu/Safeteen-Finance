# 영수증 가계부 웹 대시보드 — 리버스 하네스 (사전 조정판)

> 원본 스펙은 Flutter 모바일 캡처 앱(Part A)과 Web 대시보드(Part B)를 한 문서로 묶어 클린
> 아키텍처(3-레이어: Presentation/Domain/Data)를 양쪽에 요구했다. 이 문서는 **Part B(Web
> Dashboard)만** 이 저장소의 `www/` 실제 관례에 맞춰 다시 쓴다.
>
> **Part A(Flutter 모바일 캡처)는 이 파일의 범위가 아니다** — 문서 위치 규칙(루트
> `CLAUDE.md` "문서 위치 규칙")상 모바일 전용 내용은 `flutter/_docs/`에 별도로 둬야 한다.
> 필요하면 `flutter/_docs/s3-ocr-reverse-harness.md`를 별도로 요청해서 만든다. 참고로
> `flutter/lib/features/plant/`에 카메라·갤러리 업로드(`image_picker` 이미 의존성에 있음,
> 압축 패키지·`websocket_channel`은 아직 없음)가 이미 구현돼 있어 가장 가까운 레퍼런스다.
>
> [[fastapi/_docs/s3-ocr-reverse-harness\|백엔드 짝 문서]]가 아직 §6 미결정 사항(업로드
> 방식, S3 트리거, OCR 엔진, 실시간 통지 방식)을 확정하지 않았으므로, 이 문서의 상당수
> 항목도 그 결정에 종속적이다 — **백엔드 결정 전에는 §5 항목을 확정 구현하지 않는다.**

---

## 1. 원본 스펙과 실제 상태가 충돌하는 지점

| 원본 스펙 | 이 저장소(`www/`)의 실제 상태 |
|---|---|
| Presentation/Domain/Data 3-레이어 클린 아키텍처 | `www/`는 클린 아키텍처를 쓰지 않는다 — `app/`(라우트) + `lib/*.ts`(평평한 API 래퍼) + `components/`(UI) 3분류뿐. `www/CLAUDE.md`에 이 구조가 명시돼 있고 "테스트 하네스 없음"이 원칙 |
| 상태 관리로 BLoC/Provider(Flutter)·Zustand/React Query(Web) | `package.json`에 `@tanstack/react-query`·`zustand`·`swr` **전부 없음**. 기존 코드(`lib/plant-api.ts` + 소비하는 클라이언트 컴포넌트)는 전부 순수 `fetch` + `useState`/`useEffect` |
| S3 Direct Uploader (Presigned PUT) | 기존 업로드(`plant`, `admin`)는 전부 **`FormData` 멀티파트를 Next.js rewrite로 백엔드에 통과**시키는 방식 — 브라우저가 S3에 직접 PUT한 전례가 없다. 백엔드 하네스(§4.1)에서도 이게 아직 미확정 |
| WebSocket/SSE 리스너 | 이 코드베이스에 WebSocket·SSE 사용례가 전무하다 — 완전 신규 |
| Toast 알림 UX | `sonner`가 `package.json`에 설치돼 있고 `components/ui/toaster.tsx`/`use-toast.ts`(구형 shadcn) 컴포넌트도 존재하지만, **둘 다 `app/layout.tsx`에 배선돼 있지 않고 실사용처가 0곳**이다 — 이 기능이 사실상 첫 실사용이 된다 |

---

## 2. 재사용 가능한 기존 자산

### 2.1 API 래퍼 패턴 — `lib/plant-api.ts`

가장 가까운 기존 업로드 레퍼런스. 새 `lib/receipt-api.ts`도 이 형태를 그대로 따른다(별도 데이터 레이어·리포지토리 추상화 없이 함수 단위로 충분):

```ts
async function parseOrThrow<T>(res: Response): Promise<T> {
  const data = (await res.json().catch(() => ({}))) as T & { detail?: unknown };
  if (!res.ok) {
    const detail = typeof data?.detail === "string" ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}
```

`detail`은 백엔드 `.claude/rules/api-standards.md` 규칙대로 한국어 문자열이므로, 프론트 에러 배너에 그대로 노출해도 된다.

### 2.2 Next.js Rewrite 프록시 — `next.config.mjs`

새 엔드포인트는 `/api/receipt/:path*` → `${backendUrl}/api/receipt/:path*` 형태로 `next.config.mjs`의 `rewrites()`에 등록한다(`www/CLAUDE.md` "새 백엔드 엔드포인트 추가 시 반드시 등록" 규칙). `plant`/`admin`과 동일한 패턴.

- **주의**: `rewrites()`는 일반 HTTP 요청/응답에만 적용된다. WebSocket 업그레이드나 SSE 장기 스트림이 이 프록시 경로를 그대로 통과하는지는 검증 필요(§4.3) — 통과가 안 되면 브라우저가 `NEXT_PUBLIC_BACKEND_URL`(`api.whoareryu.cloud`) 도메인에 직접 연결해야 하고, 그 경우 CORS·쿠키(`X-User-Id` 인증) 처리를 별도로 맞춰야 한다.

### 2.3 인증 — `lib/auth.ts`

서버가 클라이언트를 식별하는 방식은 세션/쿠키 기반 로그인 후 `X-User-Id` 헤더(`www/CLAUDE.md` "API 통신" 규칙)다. 새 `/ledger` 페이지·WebSocket/SSE 연결도 이 패턴을 그대로 따른다 — 원안처럼 별도 토큰 스킴을 새로 만들지 않는다.

### 2.4 대시보드형 페이지 레퍼런스 — `app/mypage/page.tsx`

인증된 사용자 전용 목록/상태 뷰의 기존 레퍼런스. `/ledger` 페이지도 같은 폴더 관례(`app/ledger/page.tsx`, 단일 파일 + 필요시 `components/`에 도메인 컴포넌트 분리)를 따른다.

---

## 3. 조정된 구조 — 클린 아키텍처 대신 이 저장소의 3분류

```
www/
├── app/ledger/page.tsx              # Server Component 기본, 실시간 리스너는 "use client" 자식으로 분리
├── lib/receipt-api.ts               # GET /api/receipt, presigned-url 발급 요청(§4.1 확정 후)
├── lib/types/receipt.ts             # 백엔드 스키마 대응 타입 (merchantName 등은 camelCase 응답 그대로 수신)
└── components/receipt-ledger-list.tsx  # "use client" — 실시간 갱신 상태 보유
```

원안의 `Domain`(UseCase)·`Data`(Repository) 레이어는 도입하지 않는다 — `www/CLAUDE.md`가 이미 "컴포넌트에서 fetch 직접 호출 금지, `lib/` 래퍼 경유"만 요구할 뿐, 그 이상의 레이어 분리를 강제하지 않기 때문이다(요청받지 않은 아키텍처 확장 금지 원칙).

---

## 4. Part B 상세 조정

### 4.1 S3 Direct Upload — 백엔드 결정에 종속 (§6 fastapi 문서 참고)

프론트 구현이 두 갈래로 갈린다:

- **백엔드가 (A) Presigned PUT을 택하면**: `lib/receipt-api.ts`에 `requestPresignedUrl()`(→ `POST /api/receipt/presigned-url`)과 브라우저의 순수 `fetch(presignedUrl, { method: "PUT", body: file, headers: { "Content-Type": file.type } })`를 새로 추가한다. 이건 Next.js rewrite를 안 거치고 S3 도메인에 직접 쏘는 유일한 요청이 된다.
- **백엔드가 (B) 멀티파트 통과형을 유지하면**: `uploadPlantPhoto`(§2.1)와 동일하게 `FormData` + rewrite 프록시로 끝난다 — 프론트에 추가 레이어가 없다.

이 문서는 (A)/(B) 중 하나를 확정하지 않는다 — 백엔드 하네스가 결정되는 대로 이 절만 갱신한다.

### 4.2 실시간 동기화 — WebSocket vs SSE (신규, 결정 필요)

React 표준 API만으로 두 경우 모두 구현 가능하다(신규 라이브러리 불필요):

- **SSE**: `new EventSource(url, { withCredentials: true })` — 재연결이 브라우저 내장이라 클라이언트 코드가 더 단순하다. Next.js rewrite 프록시 통과 여부만 확인하면 된다.
- **WebSocket**: `new WebSocket(url)` — 재연결·핑퐁을 직접 관리해야 한다.

어느 쪽이든 연결/해제는 `/ledger` 페이지의 `"use client"` 컴포넌트 안에서 `useEffect` cleanup으로 관리한다(별도 상태 관리 라이브러리 도입 없이 `useState`로 수신 이벤트를 배열에 append).

### 4.3 자동 새로고침 목록 갱신

- 최초 진입 시 `GET /api/receipt`(REST)로 기존 로그를 채운다 — `lib/plant-api.ts`의 `fetchNotifications` 패턴과 동일.
- `RECEIPT_PROCESSED` 이벤트 수신 시 해당 `receipt_id`가 이미 목록에 있으면 교체, 없으면 맨 앞에 추가하는 단순 리듀서 로직이면 충분하다(별도 정규화 캐시 라이브러리 불필요 — 목록 규모가 가계부 단위라 React Query 캐시 계층 정당화 안 됨).

### 4.4 UX — 로딩/토스트/에러 배너

- **토스트**: `sonner`를 쓴다(이미 `package.json`에 있고 최신 shadcn 기본 선택지). `app/layout.tsx`에 `<Toaster />` 배선이 이번에 처음 들어간다 — 기존 `components/ui/toaster.tsx`(구형 shadcn `use-toast` 기반)와 **중복 도입하지 않는다**. 어느 쪽을 표준으로 할지는 실질적으로 이번 작업에서 처음 결정되는 것이므로, 구현 착수 전 확인이 필요하다(§6).
- **에러 배너**: `parseOrThrow`가 던지는 `Error.message`(한국어 `detail`)를 그대로 표시하면 된다 — 별도 에러 코드 매핑 불필요.
- **업로드 진행률**: (A) Presigned 직접 PUT을 택하면 `XMLHttpRequest.upload.onprogress`(순수 `fetch`는 업로드 진행률 이벤트 미지원)로 구현해야 한다 — 이 경우 `fetch` 대신 `XMLHttpRequest`를 그 함수 하나에만 예외적으로 쓴다.

---

## 5. 새 파일 목록 (확정 후 구현 범위)

```
www/lib/receipt-api.ts                       # requestPresignedUrl / uploadToS3 / fetchReceipts
www/lib/types/receipt.ts                      # ReceiptResult, ReceiptItem 등 백엔드 응답 타입
www/app/ledger/page.tsx                       # 서버 컴포넌트 셸
www/components/receipt-ledger-list.tsx        # "use client" — SSE/WS 리스너 + 목록 상태
www/components/receipt-upload-progress.tsx     # (A) 선택 시에만 필요
next.config.mjs                               # rewrites에 /api/receipt/:path* 추가
```

---

## 6. 미결정 사항 (구현 전 확정 필요)

| 항목 | 후보 | 비고 |
|---|---|---|
| 업로드 방식 | 백엔드 §6과 동일 결정 상속 | §4.1 |
| 실시간 채널 | SSE / WebSocket | §4.2 — 백엔드 선택과 1:1로 맞춰야 함 |
| Next.js rewrite로 스트림 프록시 가능 여부 | 프록시 통과 / 백엔드 도메인 직접 연결 | 실제 검증(로컬 dev 서버 + 프로덕션 Cloudflare Tunnel 양쪽) 필요 |
| 토스트 컴포넌트 표준화 | `sonner` / 기존 `components/ui/toaster.tsx` | 이번이 첫 실배선이라 표준을 여기서 정하게 됨 |
| `/ledger` 진입 권한 | 로그인 필수 여부, `role` 제한 여부 | 기존 `mypage`처럼 로그인 사용자 전용으로 볼지 확인 필요 |

---

## 관련 문서

[[fastapi/_docs/s3-ocr-reverse-harness\|백엔드 짝 문서]] · [[www/CLAUDE\|Frontend CLAUDE]] · [[www/_docs/CLAUDE\|Frontend Docs 인덱스]] · [[_docs/architecture\|Master Architecture]]
