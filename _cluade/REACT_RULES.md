# Frontend React 규칙 (GourmetMate)

이 문서는 **Cursor / 코딩 에이전트**가 프론트엔드 React 코드를 작성·리팩터할 때 따를 규칙입니다.  
매번 같은 프롬프트를 치지 않아도 되도록, `backend/.cursorrules` → `docs/README.md` → **본 문서** 순으로 참조합니다.

---

## 1. `useState`는 많이 쓰지 않는다

- 관련된 UI·폼·로딩·에러 상태는 **여러 개의 `useState`로 쪼개지 말고**, **하나의 객체 상태**로 묶는다.
- 예: `username`, `password`, `error`, `submitting` → `AuthFormState` + `useState<AuthFormState>(...)`
- 부분 갱신은 **스프레드 + `patch` 헬퍼**로 한다.

```tsx
const [state, setState] = useState<FormState>(initialState);

const patch = (partial: Partial<FormState>) => {
  setState((prev) => ({ ...prev, ...partial }));
};

// 사용
patch({ error: null, submitting: true });
```

### 피해야 할 패턴

```tsx
const [username, setUsername] = useState("");
const [password, setPassword] = useState("");
const [error, setError] = useState<string | null>(null);
const [submitting, setSubmitting] = useState(false);
// ... 10개 이상의 useState
```

### 권장 패턴

```tsx
type FormState = {
  username: string;
  password: string;
  error: string | null;
  submitting: boolean;
};

const [state, setState] = useState<FormState>(createInitialState());
const { username, password, error, submitting } = state;
```

**예외:** 서로 무관하고 한 컴포넌트에서 한 번도 같이 갱신되지 않는 상태만 별도 `useState` 허용.

---

## 2. 폼 제출은 `FormData` + `name` 속성

제출 시점 값은 `FormData`로 읽고, 입력 중 표시는 객체 상태로 **controlled** 유지한다.

### 참조 코드 (회원가입 / 로그인)

```tsx
const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
  const formProps = Object.fromEntries(formData.entries()) as {
    username: string;
    password: string;
    password_confirm: string;
    email: string;
    nickname: string;
  };

  const id = formProps.username.trim();
  // formProps.password, formProps.email 등 사용
};

const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
  const formProps = Object.fromEntries(formData.entries()) as {
    username: string;
    password: string;
  };
  await login(formProps.username.trim(), formProps.password);
};
```

### 입력 필드

- 각 `<input>` 에 **`name`** 과 **`value` / `onChange`** 를 둔다.
- `name` 이 camelCase 상태 키와 다르면 (예: `password_confirm` → `passwordConfirm`) `onChange` 에서 매핑한다.

```tsx
<input
  name="password_confirm"
  value={state.passwordConfirm}
  onChange={handleFieldChange}
/>
```

---

## 3. 에이전트에게 줄 표준 프롬프트 (복사용)

아래 블록을 그대로 Cursor에 붙여 넣어도 되고, **이 파일을 `@` 로 첨부**하면 동일한 지시로 처리한다.

```text
리액트에서 useState는 많이 사용하면 안 됩니다.
다음 코드를 참조하여, 여러 개의 useState를 useState 객체 하나로 압축하는 코드로 변경해줘.

const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
  const formProps = Object.fromEntries(formData.entries());
};

@docs/DevOps/Frontend/REACT_RULES.md 규칙을 따르세요.
```

---

## 4. 입력 데이터를 노출하는 `alert` 금지

**비밀번호·이메일·아이디 등 사용자 입력값을 `alert` / `confirm` / `prompt` 로 보여주지 않는다.**  
디버깅·데모용이라도 프로덕션 코드에 남기지 않는다.

### 금지 (제거 대상)

```tsx
// ❌ 절대 사용하지 않음 — 폼 값·비밀번호가 그대로 노출됨
window.alert(
  [
    "입력하신 내용",
    `아이디: ${username}`,
    `비밀번호: ${password}`,
    `이메일: ${email}`,
  ].join("\n")
);

alert(JSON.stringify(formProps, null, 2));
console.log("signup payload", formProps); // 배포 코드에서도 민감 필드 로그 금지
```

### 허용되는 피드백

- 폼 아래 **인라인 메시지** (`role="alert"`, `state.error`)
- 토스트/배너는 **일반 문구만** (예: 「회원가입이 완료되었습니다」)
- 검증 실패는 필드 옆·`patch({ error: "..." })` 로 처리

```tsx
if (formProps.password !== formProps.password_confirm) {
  patch({ error: "비밀번호가 일치하지 않습니다." });
  return;
}

patch({ submitting: true, error: null });
try {
  await signup({ ... });
  resetAndClose();
} catch (err) {
  patch({
    error: err instanceof Error ? err.message : "회원가입에 실패했습니다.",
  });
}
```

### 리팩터 시 검색

프론트엔드 변경·리뷰 전에 아래를 검색해 **입력 노출 alert 가 있으면 삭제**한다.

```text
alert(
window.alert(
confirm(
prompt(
```

### 에이전트 표준 프롬프트 (복사용)

```text
@docs/DevOps/Frontend/REACT_RULES.md §4를 따르세요.
입력 데이터(비밀번호, 이메일, 아이디 등)가 노출되는 alert / window.alert / confirm 을 전부 제거하고,
에러·성공 안내는 인라인 UI(state.error 등)로만 표시해 주세요.
```

---

## 5. 리팩터 체크리스트

에이전트·리뷰어는 변경 후 아래를 확인한다.

- [ ] 관련 `useState` 가 **1개 객체** (+ 필요 시 `patch`) 로 합쳐졌는가?
- [ ] `createInitialState()` / `reset` 시 객체를 **통째로** 초기화하는가?
- [ ] `handleSubmit` 이 `React.FormEvent<HTMLFormElement>` + `FormData` 를 쓰는가?
- [ ] 폼 필드에 `name` 이 있고, 제출 payload 와 일치하는가?
- [ ] 불필요한 개별 setter (`setUsername` 등) 가 남지 않았는가?
- [ ] **`alert` / `window.alert` 에 폼·비밀번호·개인정보가 들어가지 않는가?**

---

## 6. 프로젝트 내 적용 예

- `frontend/components/auth-modal.tsx` — `AuthModalState` + `patch` + `FormData` 제출, **입력 노출 alert 없음**

새 모달·설정 폼·다단계 폼도 위 패턴을 기본으로 한다.

---

## 관련 문서

[[www/_cluade/CLAUDE\|Frontend CLAUDE]] · [[VERCEL_V0_DEPLOY]]
