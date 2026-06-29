/** GPS 방문 감지 — 추천 식당 타깃 저장 + 방문 확인 API (기획서 4-2). */

function userHeader(userId: number): Record<string, string> {
  return { "X-User-Id": String(userId) };
}

const TARGET_KEY = "gm:visit-target";

export type VisitTarget = {
  id: number;
  name: string;
  genre: string;
  latitude: number;
  longitude: number;
};

export function setVisitTarget(target: VisitTarget): void {
  try {
    localStorage.setItem(TARGET_KEY, JSON.stringify(target));
  } catch {
    /* localStorage 불가 환경 무시 */
  }
}

export function getVisitTarget(): VisitTarget | null {
  try {
    const raw = localStorage.getItem(TARGET_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as VisitTarget;
  } catch {
    return null;
  }
}

/** 두 좌표 사이 거리(m) — Haversine. */
export function distanceMeters(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number,
): number {
  const R = 6371000;
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

export async function confirmVisit(
  userId: number,
  body: {
    restaurant_id: number;
    rating: number | null;
    latitude?: number;
    longitude?: number;
  },
): Promise<void> {
  const res = await fetch("/api/gourmet/visits", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...userHeader(userId) },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`방문 저장 실패: ${res.status}`);
}
