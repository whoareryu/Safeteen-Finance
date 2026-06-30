/** 온보딩 API 래퍼 (백엔드 /gourmet/onboarding, X-User-Id 인증). */

const _key = (userId: number) => `onboarding_done_${userId}`;

export function markOnboardingDone(userId: number) {
  if (typeof window === "undefined") return;
  localStorage.setItem(_key(userId), "1");
}

export function isOnboardingLocallyDone(userId: number): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(_key(userId)) === "1";
}

export type OnboardingPayload = {
  genre_ranking: string[];
  dining_mode: string;
  portion: string;
  allergies: string[];
  avoid_foods: string[];
  use_budget: boolean;
  monthly_budget: number | null;
};

export type UserPreference = OnboardingPayload & { completed: boolean };

function userHeader(userId: number): Record<string, string> {
  return { "X-User-Id": String(userId) };
}

export async function fetchMyPreference(userId: number): Promise<UserPreference> {
  const res = await fetch("/api/gourmet/onboarding/me", {
    headers: userHeader(userId),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`온보딩 조회 실패: ${res.status}`);
  return (await res.json()) as UserPreference;
}

export async function submitOnboarding(
  userId: number,
  payload: OnboardingPayload,
): Promise<UserPreference> {
  const res = await fetch("/api/gourmet/onboarding", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...userHeader(userId) },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`온보딩 저장 실패: ${res.status}`);
  return (await res.json()) as UserPreference;
}
