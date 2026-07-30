---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript 규칙

`www/`에서 실제로 쓰이고 있는 패턴을 기준으로 한다. 새 코드는 아래를 따르고,
기존 파일을 수정할 때는 그 파일의 스타일을 우선한다 (루트 CLAUDE.md §3 정밀한 수정).

---

## 1. 기본

- **strict mode 필수.** `www/tsconfig.json`의 `"strict": true`를 끄지 않는다.
- **`any` 금지.** 외부에서 들어온 값은 `unknown`으로 받고 좁혀서 쓴다.
- **타입 별칭(`type`)을 기본으로 쓴다.** `interface`는 `lib/`의 순수 데이터 모델에서만 유지한다.
- `enum`을 쓰지 않는다. 유니언 리터럴 또는 `as const` 객체로 대체한다.

`next.config.mjs`의 `typescript.ignoreBuildErrors: true`는 의도된 설정이지만,
**타입 에러를 방치해도 된다는 뜻은 아니다.** 빌드가 통과해도 타입은 맞춰 놓는다.

---

## 2. 타입 별칭 우선

선언은 `type`을 기본으로 한다.

```ts
// components/gemini-chat.tsx
type Role = "user" | "assistant";
type Msg = { id: string; role: Role; content: string };
type AttachedImage = { file: File; previewUrl: string };
```

`interface`는 `lib/`의 순수 데이터 모델처럼 이미 그렇게 선언된 곳에서만 유지한다
(`lib/titanic.ts`의 `ChatMessage`/`SmithChatResponse`, `lib/plant-api.ts`,
`lib/chef-address.ts`). 새로 만드는 타입은 `type`으로 쓴다. 선언 병합(declaration
merging)이 필요한 경우에만 `interface`가 정당한 선택이다.

---

## 3. `unknown` 우선, `any` 금지

API 응답은 `unknown`을 포함한 형태로 받고 좁혀서 쓴다. `lib/` 전반에서 반복되는
패턴:

```ts
// lib/plant-api.ts, lib/my-plants-api.ts, lib/plant-tutorial-api.ts, lib/crawler-api.ts 공통 패턴
const data = (await res.json().catch(() => ({}))) as T & { detail?: unknown };
```

에러는 `instanceof`로 좁힌다.

```ts
// app/api/titanic/smith-chat/route.ts
const message = e instanceof Error ? e.message : "오류가 발생했습니다.";
```

---

## 4. 컴포넌트 Props

- Props는 `<컴포넌트명>Props` 이름의 `type`으로 선언한다.
- 컴포넌트는 **default export** 함수 선언이 다수다 (`export default function Xxx`).
  기존 파일이 named export면 그 스타일을 따른다.
- 선택 값은 `?`와 기본값으로 처리하고, JSDoc 주석으로 기본 동작을 남긴다.

```tsx
// components/gemini-chat.tsx
type GeminiChatProps = {
  variant?: "dark" | "apple";
  /** 기본 `/api/chat` — 타이타닉은 `/api/titanic/chat` */
  apiPath?: string;
  inputPlaceholder?: string;
  onImageAttach?: (file: File) => Promise<string>;
};

export default function GeminiChat({
  variant = "dark",
  apiPath = "/api/chat",
  inputPlaceholder = "무엇이든 물어보세요",
  onImageAttach,
}: GeminiChatProps) {
  // ...
}
```

`components/ui/`(shadcn 자동생성)는 직접 수정하지 않는다. 그쪽은 DOM 속성을
`React.ComponentProps<'button'> & VariantProps<typeof buttonVariants>`처럼
확장하는 shadcn 관례를 따르며, 우리 규칙보다 생성기 출력이 우선이다.

---

## 5. 상수는 `as const`, 타입은 거기서 파생

값과 타입을 두 번 적지 않는다.

```tsx
// components/gemini-chat.tsx 스타일
const ROLES = ["user", "assistant"] as const;
type Role = (typeof ROLES)[number];
```

---

## 6. 훅 타이핑

- `useState`는 초기값으로 추론되지 않을 때만 제네릭을 붙인다.
  - `useState("")` → 제네릭 불필요
  - `useState<Msg[]>([])`, `useState<string | null>(null)` → 필요
- `useRef`는 DOM 엘리먼트 타입을 명시한다: `useRef<HTMLTextAreaElement>(null)`
  (`app/portfolio/langchain/chat/page.tsx` 참고).

```tsx
// app/portfolio/langchain/chat/page.tsx
const [messages, setMessages] = useState<Msg[]>([INITIAL]);
const textareaRef = useRef<HTMLTextAreaElement>(null);
const isComposingRef = useRef(false);
```

---

## 7. Route Handler (`app/api/**/route.ts`)

두 패턴이 실제로 쓰인다.

**(a) 백엔드로 그대로 넘기는 얇은 프록시** — 대부분 이 형태다. 로직은
`lib/backend-proxy.ts`의 `proxyToBackend`에 있다.

```ts
// app/api/chat/route.ts
import { proxyToBackend } from "@/lib/backend-proxy";

export async function POST(request: Request) {
  return proxyToBackend(request, "/chat");
}
```

**(b) 요청 본문을 가공해서 넘기는 경우** — 파싱 전에 기대 형태를 선언하고,
`req.json()` 실패와 백엔드 호출 실패를 각각 잡는다.

```ts
// app/api/titanic/smith-chat/route.ts
export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { message?: string };
    const userMessage = (body.message ?? "").trim();
    if (!userMessage) {
      return NextResponse.json({ error: "메시지를 입력해 주세요." }, { status: 400 });
    }
    // ... 백엔드 호출
  } catch (e) {
    const message = e instanceof Error ? e.message : "오류가 발생했습니다.";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
```

새 백엔드 프록시 라우트를 추가할 때는 (a)를 우선 고려하고, 요청/응답 가공이
필요할 때만 (b)로 간다. 에러 메시지는 사용자에게 노출되므로 **한국어**로 쓰고,
백엔드 URL·내부 정보를 그대로 흘리지 않는다 (`lib/backend-proxy.ts`의
`backendNotConfiguredResponse` 참고).

---

## 8. import

- 타입 전용 import는 `import type` 또는 인라인 `type` 지정자를 쓴다.
  `isolatedModules: true`이므로 이 구분이 필요하다.
- 프로젝트 내부 참조는 경로 별칭 `@/`를 쓴다 (`@/lib/utils`, `@/components/ui/button`).
  같은 디렉터리 내부 참조에만 상대 경로를 허용한다.
- 클라이언트 컴포넌트는 파일 최상단에 `"use client";`를 둔다. 상태·이벤트·브라우저
  API가 필요 없으면 붙이지 않는다 (App Router 기본은 서버 컴포넌트).

---

## 9. 컴포넌트에서 직접 `fetch` 금지

`www/CLAUDE.md` 규약: 컴포넌트에서 `fetch` 직접 호출 금지, `lib/` 래퍼를 경유한다
(예외: `app/portfolio/langchain/chat/page.tsx`처럼 백엔드 라우트 하나만 호출하는
단순 페이지는 현재 직접 `fetch`를 쓰고 있다 — 새로 만들 때는 `lib/` 래퍼를 우선
검토한다).

---

## 10. 체크리스트

새 `.ts` / `.tsx` 파일을 추가하거나 수정했다면:

- [ ] `any`가 없다 (`unknown` + 좁히기로 해결했다)
- [ ] 새 타입은 `type` 별칭으로 선언했다
- [ ] Props 타입 이름이 `<컴포넌트명>Props`다
- [ ] 상수 리터럴에 `as const`를 붙이고 타입을 파생시켰다
- [ ] 타입 전용 import에 `type` 지정자를 붙였다
- [ ] 내부 import가 `@/` 별칭을 쓴다
- [ ] 새 API 프록시는 가능하면 `lib/backend-proxy.ts`의 `proxyToBackend`를 썼다
- [ ] `pnpm build`가 통과한다 (`www`에는 ESLint 설정이 없어 `pnpm lint`는 검증 수단이 아니다)
