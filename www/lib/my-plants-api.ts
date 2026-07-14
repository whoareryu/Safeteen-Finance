export interface MyPlant {
  id: number;
  nickname: string;
  species_name: string;
  region: string;
  growth_stage: string;
  points: number;
  streak_count: number;
}

export interface CheckinResult {
  id: number;
  plant_id: number;
  checkin_date: string;
  health_score: number;
  points_earned: number;
  streak_day: number;
  total_points: number;
  growth_stage: string;
  new_badges: string[];
}

export interface CheckinHistoryItem {
  id: number;
  photo_url: string;
  checkin_date: string;
  health_score: number;
  points_earned: number;
  streak_day: number;
}

export interface Badge {
  code: string;
  name: string;
  description: string;
  icon: string;
  earned: boolean;
  earned_at: string | null;
}

export interface LeaderboardEntry {
  rank: number;
  plant_id: number;
  nickname: string;
  species_name: string;
  points: number;
  growth_stage: string;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  const data = (await res.json().catch(() => ({}))) as T & { detail?: unknown };
  if (!res.ok) {
    const detail = typeof data?.detail === "string" ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

export async function registerMyPlant(params: {
  region: string;
  speciesName?: string;
  photo?: File;
  ownerUserId?: number;
}): Promise<MyPlant> {
  const formData = new FormData();
  formData.append("region", params.region);
  if (params.speciesName) formData.append("species_name", params.speciesName);
  if (params.ownerUserId != null) formData.append("owner_user_id", String(params.ownerUserId));
  if (params.photo) formData.append("file", params.photo);

  const res = await fetch("/api/plant/my-plants", { method: "POST", body: formData });
  return parseOrThrow<MyPlant>(res);
}

export async function listMyPlants(ownerUserId?: number): Promise<MyPlant[]> {
  const qs = ownerUserId != null ? `?owner_user_id=${ownerUserId}` : "";
  const res = await fetch(`/api/plant/my-plants${qs}`);
  return parseOrThrow<MyPlant[]>(res);
}

export async function getMyPlant(plantId: number): Promise<MyPlant> {
  const res = await fetch(`/api/plant/my-plants/${plantId}`);
  return parseOrThrow<MyPlant>(res);
}

export async function checkinMyPlant(plantId: number, photo: File): Promise<CheckinResult> {
  const formData = new FormData();
  formData.append("file", photo);
  const res = await fetch(`/api/plant/my-plants/${plantId}/checkin`, {
    method: "POST",
    body: formData,
  });
  return parseOrThrow<CheckinResult>(res);
}

export async function listCheckins(plantId: number): Promise<CheckinHistoryItem[]> {
  const res = await fetch(`/api/plant/my-plants/${plantId}/checkins`);
  return parseOrThrow<CheckinHistoryItem[]>(res);
}

export async function listBadges(plantId: number): Promise<Badge[]> {
  const res = await fetch(`/api/plant/my-plants/${plantId}/badges`);
  return parseOrThrow<Badge[]>(res);
}

export async function getLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
  const res = await fetch(`/api/plant/leaderboard?limit=${limit}`);
  return parseOrThrow<LeaderboardEntry[]>(res);
}
