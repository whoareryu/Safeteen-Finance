export interface DiagnosisResult {
  id: number;
  plant_id: number;
  photo_url: string;
  detected_species: string;
  species_confidence: number;
  symptom_label: string;
  symptom_confidence: number;
}

export interface CareGuideResult {
  id: number;
  diagnosis_record_id: number;
  prescription_text: string;
}

export interface WeatherSnapshot {
  id: number;
  region: string;
  temp_c: number;
  humidity_pct: number;
  sunlight_desc: string;
  is_dry_day: boolean;
}

export interface NotificationEvent {
  id: number;
  plant_id: number | null;
  channel: string;
  message: string;
  coupang_link: string | null;
  delivery_status: string;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  const data = (await res.json().catch(() => ({}))) as T & { detail?: unknown };
  if (!res.ok) {
    const detail = typeof data?.detail === "string" ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

export async function uploadPlantPhoto(
  file: File,
  region: string,
  ownerUserId?: number
): Promise<DiagnosisResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("region", region);
  if (ownerUserId != null) formData.append("owner_user_id", String(ownerUserId));

  const res = await fetch("/api/plant/diagnosis/upload", {
    method: "POST",
    body: formData,
  });
  return parseOrThrow<DiagnosisResult>(res);
}

export async function fetchDiagnosis(id: number): Promise<DiagnosisResult> {
  const res = await fetch(`/api/plant/diagnosis/${id}`);
  return parseOrThrow<DiagnosisResult>(res);
}

export async function generateCareGuide(diagnosisId: number): Promise<CareGuideResult> {
  const res = await fetch(`/api/plant/diagnosis/${diagnosisId}/care-guide`, {
    method: "POST",
  });
  return parseOrThrow<CareGuideResult>(res);
}

export async function fetchWeatherStatus(region: string): Promise<WeatherSnapshot> {
  const res = await fetch(`/api/plant/weather/current?region=${encodeURIComponent(region)}`);
  return parseOrThrow<WeatherSnapshot>(res);
}

export async function fetchNotifications(plantId: number): Promise<NotificationEvent[]> {
  const res = await fetch(`/api/plant/notifications?plant_id=${plantId}`);
  return parseOrThrow<NotificationEvent[]>(res);
}
