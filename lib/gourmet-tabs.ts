/** 탭(커플·여행 코스 / 헬스 식단) API 래퍼. */

export type CourseStop = { slot: string; restaurant_id: number; name: string };
export type CourseResult = { district: string; stops: CourseStop[] };

export async function fetchCourse(
  district: string,
  partyType = "couple",
): Promise<CourseResult> {
  const params = new URLSearchParams({ district, party_type: partyType });
  const res = await fetch(`/api/gourmet/course?${params.toString()}`);
  if (!res.ok) throw new Error(`코스 요청 실패: ${res.status}`);
  return (await res.json()) as CourseResult;
}

export type DietRestaurant = {
  id: number;
  name: string;
  genre: string;
  road_address: string;
  latitude: number | null;
  longitude: number | null;
};
export type DietResult = { diet_type: string; restaurants: DietRestaurant[] };

export async function fetchDiet(
  dietType: string,
  district?: string,
): Promise<DietResult> {
  const params = new URLSearchParams({ diet_type: dietType });
  if (district) params.set("district", district);
  const res = await fetch(`/api/gourmet/diet?${params.toString()}`);
  if (!res.ok) throw new Error(`식단 요청 실패: ${res.status}`);
  return (await res.json()) as DietResult;
}
