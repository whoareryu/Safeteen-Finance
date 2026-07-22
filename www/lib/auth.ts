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

export async function updateNickname(nickname: string): Promise<AuthUser> {
  const res = await authFetch("/api/auth/nickname", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nickname }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AuthUser;
}

/** OAuth 신규 가입자가 닉네임 설정·약관 동의를 완료하면 계정을 생성하고 세션을 시작한다. */
export async function completeConsent(
  consentToken: string,
  nickname: string,
  agreeTerms: boolean
): Promise<AuthUser> {
  const res = await authFetch("/api/auth/consent/complete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      consent_token: consentToken,
      nickname,
      agree_terms: agreeTerms,
    }),
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
