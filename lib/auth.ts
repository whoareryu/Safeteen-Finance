export type AuthUser = {
  username: string;
  nickname: string;
  email: string;
};

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
  const res = await authFetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AuthUser;
}
