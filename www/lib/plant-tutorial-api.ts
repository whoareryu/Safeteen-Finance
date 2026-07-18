export interface TutorialSpecies {
  name: string;
  label: string;
}

export const TUTORIAL_SPECIES: TutorialSpecies[] = [
  { name: "몬스테라", label: "몬스테라" },
  { name: "스킨답서스", label: "스킨답서스" },
  { name: "산세베리아", label: "산세베리아" },
  { name: "스투키", label: "스투키" },
  { name: "홍콩야자", label: "홍콩야자" },
  { name: "선인장", label: "선인장" },
];

export const TUTORIAL_REGIONS = ["서울", "부산", "인천", "대구", "대전", "광주", "울산", "수원", "제주"];

export interface TutorialState {
  id: number;
  owner_user_id: number;
  species_name: string;
  region: string;
  growth_stage: string;
  soil_moisture_pct: number;
  nutrient_pct: number;
  light_position: string;
  points: number;
  status: string;
  photo_url: string;
  feedback: string | null;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  const data = (await res.json().catch(() => ({}))) as T & { detail?: unknown };
  if (!res.ok) {
    const detail = typeof data?.detail === "string" ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

export async function createTutorialPlant(
  speciesName: string,
  region: string,
  ownerUserId: number
): Promise<TutorialState> {
  const res = await fetch("/api/plant/tutorial", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ species_name: speciesName, region, owner_user_id: ownerUserId }),
  });
  return parseOrThrow<TutorialState>(res);
}

export async function getActiveTutorialPlant(ownerUserId: number): Promise<TutorialState | null> {
  const res = await fetch(`/api/plant/tutorial/active?owner_user_id=${ownerUserId}`);
  return parseOrThrow<TutorialState | null>(res);
}

export async function waterTutorialPlant(id: number): Promise<TutorialState> {
  const res = await fetch(`/api/plant/tutorial/${id}/water`, { method: "POST" });
  return parseOrThrow<TutorialState>(res);
}

export async function addNutrientTutorialPlant(id: number): Promise<TutorialState> {
  const res = await fetch(`/api/plant/tutorial/${id}/nutrient`, { method: "POST" });
  return parseOrThrow<TutorialState>(res);
}

export async function moveLightTutorialPlant(id: number, lightPosition: string): Promise<TutorialState> {
  const res = await fetch(`/api/plant/tutorial/${id}/move-light`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ light_position: lightPosition }),
  });
  return parseOrThrow<TutorialState>(res);
}

export async function checkLeavesTutorialPlant(id: number): Promise<TutorialState> {
  const res = await fetch(`/api/plant/tutorial/${id}/check-leaves`);
  return parseOrThrow<TutorialState>(res);
}
