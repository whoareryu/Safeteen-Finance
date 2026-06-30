/** 메인 홈 "오늘의 추천 1곳" API 래퍼 (백엔드 /gourmet/recommendation/today). */

export type TimeSlot = "morning" | "lunch" | "dinner";

export type RecommendationCard = {
  id: number;
  name: string;
  genre: string;
  road_address: string;
  latitude: number | null;
  longitude: number | null;
  reason: string;
  time_slot: string;
};

export type DiningMode = "dine_in" | "pickup" | "delivery";

export const DINING_MODE_LABEL: Record<DiningMode, string> = {
  dine_in: "매장식사",
  pickup: "포장",
  delivery: "배달",
};

export type RecommendationRequest = {
  time_slot?: TimeSlot;
  weather?: string;
  excluded_ids?: number[];
  genre_ranking?: string[];
  lat?: number | null;
  lng?: number | null;
  dining_mode?: DiningMode | null;
};

/** 06~10 아침 / 10~16 점심 / 그 외 저녁 (기획서 3-2). */
export function currentTimeSlot(date = new Date()): TimeSlot {
  const hour = date.getHours();
  if (hour >= 6 && hour < 10) return "morning";
  if (hour >= 10 && hour < 16) return "lunch";
  return "dinner";
}

export const TIME_SLOT_LABEL: Record<TimeSlot, string> = {
  morning: "🌅 아침 추천",
  lunch: "☀️ 점심 추천",
  dinner: "🌙 저녁 추천",
};

/** 추천 1곳 요청. 후보가 없으면 null. */
export async function fetchTodayRecommendation(
  body: RecommendationRequest,
): Promise<RecommendationCard | null> {
  const res = await fetch("/api/gourmet/recommendation/today", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`추천 요청 실패: ${res.status}`);
  return (await res.json()) as RecommendationCard;
}
