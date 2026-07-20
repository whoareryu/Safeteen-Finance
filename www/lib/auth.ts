export type UserRole = "admin" | "user" | "partner";

export type AuthUser = {
  id: number;
  username: string;
  nickname: string;
  email: string;
  role: UserRole;
  region?: string | null;
};

export function isAdmin(user: AuthUser | null | undefined): boolean {
  return user?.role === "admin";
}

/** Naver·Kakao 팝업 로그인 완료 시 팝업→부모 창으로 postMessage할 때 쓰는 타입 문자열. */
export const WR_AUTH_COMPLETE_MESSAGE = "wr-auth-complete";

export type AvailabilityResult = {
  available: boolean;
  message: string;
};

const STORAGE_KEY = "whoareryu_auth_user";

export function loadStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as AuthUser;
    if (!parsed?.username || !parsed?.nickname) return null;
    if (!parsed.role) parsed.role = "user";
    if (typeof parsed.id !== "number") return null;
    return parsed;
  } catch {
    return null;
  }
}

/** 로그인 사용자 API — ``X-User-Id`` (백엔드 ``GET /auth/me`` 등). */
export function authHeaders(user: AuthUser | null): HeadersInit {
  if (!user?.id) return {};
  return { "X-User-Id": String(user.id) };
}

export async function fetchCurrentUser(userId: number): Promise<AuthUser | null> {
  const res = await authFetch("/api/auth/me", {
    headers: { "X-User-Id": String(userId) },
  });
  if (!res.ok) return null;
  return (await res.json()) as AuthUser;
}

export function saveStoredUser(user: AuthUser | null) {
  if (typeof window === "undefined") return;
  if (user) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as {
      detail?: string | { msg?: string }[] | { msg?: string };
      message?: string;
    };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      const first = body.detail[0];
      if (first && typeof first === "object" && "msg" in first && first.msg)
        return first.msg;
    }
    if (body.message) return body.message;
  } catch {
    /* ignore */
  }
  return "요청 처리에 실패했습니다.";
}

async function authFetch(path: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(path, init);
  } catch {
    throw new Error(
      "서버에 연결할 수 없습니다. 백엔드를 실행했는지 확인해 주세요. (uvicorn apps.main:app --reload)"
    );
  }
}

export async function checkUsernameAvailable(
  username: string
): Promise<AvailabilityResult> {
  const res = await authFetch(
    `/api/auth/check-username?username=${encodeURIComponent(username.trim())}`
  );
  if (!res.ok) throw new Error(await parseError(res));
  const data = (await res.json()) as AvailabilityResult & { username?: string };
  return { available: data.available, message: data.message };
}

export async function checkNicknameAvailable(
  nickname: string
): Promise<AvailabilityResult> {
  const res = await authFetch(
    `/api/auth/check-nickname?nickname=${encodeURIComponent(nickname.trim())}`
  );
  if (!res.ok) throw new Error(await parseError(res));
  const data = (await res.json()) as AvailabilityResult & { nickname?: string };
  return { available: data.available, message: data.message };
}

export async function signup(payload: {
  username: string;
  password: string;
  password_confirm: string;
  email: string;
  nickname: string;
  region?: string;
  agree_terms: boolean;
}): Promise<AuthUser> {
  const res = await authFetch("/api/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AuthUser;
}

export async function login(username: string, password: string): Promise<AuthUser> {
  const res = await authFetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AuthUser;
}

export type GoogleLoginResult = AuthUser & { is_owner: boolean; pending?: false };

/** 계정이 아직 없는 신규 가입자 — 약관 동의(/auth/consent)를 먼저 거쳐야 한다. */
export type PendingConsentResult = {
  pending: true;
  consent_token: string;
  email: string;
  nickname: string;
};

export async function googleLogin(
  credential: string
): Promise<GoogleLoginResult | PendingConsentResult> {
  const res = await authFetch("/api/auth/google", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credential }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as GoogleLoginResult | PendingConsentResult;
}

/** OAuth 신규 가입자가 약관 동의를 완료하면 계정을 생성하고 세션을 시작한다. */
export async function completeConsent(
  consentToken: string,
  agreeTerms: boolean
): Promise<AuthUser> {
  const res = await authFetch("/api/auth/consent/complete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ consent_token: consentToken, agree_terms: agreeTerms }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AuthUser;
}

/** 소유자(owner) 전용 기능(이메일 발송·주소록·lesson 탭) 접근 가능 여부. */
export async function checkOwner(): Promise<boolean> {
  try {
    const res = await authFetch("/api/auth/owner-check");
    if (!res.ok) return false;
    const data = (await res.json()) as { is_owner: boolean };
    return data.is_owner;
  } catch {
    return false;
  }
}

/** httpOnly wr_session 쿠키(JWT+Redis)로 현재 로그인 사용자를 복원한다. 세션 없으면 null. */
export async function fetchSession(): Promise<AuthUser | null> {
  try {
    const res = await authFetch("/api/auth/session");
    if (!res.ok) return null;
    return (await res.json()) as AuthUser;
  } catch {
    return null;
  }
}

export async function logoutSession(): Promise<void> {
  await authFetch("/api/auth/logout", { method: "POST" });
}
