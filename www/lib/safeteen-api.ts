export type RiskLevel = "SAFE" | "WARNING" | "DANGER";

export type AlternativePolicy = {
  title: string;
  description: string;
  official_link: string;
};

export type AnalysisRequest = {
  text?: string | null;
  file?: File | null;
};

export type AnalysisResult = {
  risk_level: RiskLevel;
  risk_score: number;
  detected_terms: string[];
  crime_type: string;
  legal_warning: string;
  fact_check_summary: string;
  alternative_policy: AlternativePolicy | null;
};

export type EmergencyGuideRequest = {
  situation?: string | null;
};

export type EmergencyStep = {
  order: number;
  title: string;
  description: string;
};

export type EmergencyHotline = {
  name: string;
  phone_number: string;
  description: string;
};

export type EmergencyGuide = {
  account_freeze_steps: EmergencyStep[];
  police_report_steps: EmergencyStep[];
  hotlines: EmergencyHotline[];
};

export type IncidentReportRequest = {
  situation: string;
  file?: File | null;
};

export type IncidentReportResult = {
  incident_summary: string;
  victim_statement: string;
  evidence_list: string[];
  requested_action: string;
};

async function parseOrThrow<T>(res: Response): Promise<T> {
  const data = (await res.json().catch(() => ({}))) as T & { detail?: unknown };
  if (!res.ok) {
    const detail = typeof data?.detail === "string" ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

export async function analyzeContent(request: AnalysisRequest): Promise<AnalysisResult> {
  const formData = new FormData();
  if (request.text) formData.set("text", request.text);
  if (request.file) formData.set("file", request.file);

  // FormData의 Content-Type(multipart boundary 포함)은 fetch가 자동으로 채우므로 직접 지정하지 않는다.
  const res = await fetch("/api/safeteen/analyze", {
    method: "POST",
    body: formData,
  });
  return parseOrThrow<AnalysisResult>(res);
}

export async function listPolicies(): Promise<AlternativePolicy[]> {
  const res = await fetch("/api/safeteen/policies", { cache: "no-store" });
  return parseOrThrow<AlternativePolicy[]>(res);
}

export async function fetchEmergencyGuide(request: EmergencyGuideRequest = {}): Promise<EmergencyGuide> {
  const res = await fetch("/api/safeteen/emergency-guide", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  return parseOrThrow<EmergencyGuide>(res);
}

export async function generateIncidentReport(request: IncidentReportRequest): Promise<IncidentReportResult> {
  const formData = new FormData();
  formData.set("situation", request.situation);
  if (request.file) formData.set("file", request.file);

  const res = await fetch("/api/safeteen/incident-report", {
    method: "POST",
    body: formData,
  });
  return parseOrThrow<IncidentReportResult>(res);
}
