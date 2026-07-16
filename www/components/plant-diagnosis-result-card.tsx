"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { generateCareGuide, type DiagnosisResult } from "@/lib/plant-api";
import { translateSpecies, translateSymptom } from "@/lib/plant-labels";

export default function PlantDiagnosisResultCard({ diagnosis }: { diagnosis: DiagnosisResult }) {
  const [loading, setLoading] = useState(false);
  const [prescription, setPrescription] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onGenerateCareGuide = async () => {
    setLoading(true);
    setError(null);
    try {
      const guide = await generateCareGuide(diagnosis.id);
      setPrescription(guide.prescription_text);
    } catch (e) {
      setError(e instanceof Error ? e.message : "케어 처방 생성 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="plant-diagnosis-result-card saessak-card w-full max-w-none p-6">
      <img
        src={diagnosis.photo_url}
        alt="진단한 잎사귀 사진"
        className="max-h-60 w-full rounded-2xl object-contain"
      />

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-accent px-3 py-1 text-sm font-semibold text-accent-foreground">
          {translateSpecies(diagnosis.detected_species)}
        </span>
        <span className="rounded-full bg-secondary px-3 py-1 text-sm font-medium text-secondary-foreground">
          {translateSymptom(diagnosis.symptom_label)}
        </span>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-border bg-muted/50 px-3 py-2.5 text-center">
          <dt className="text-xs text-muted-foreground">품종 확신도</dt>
          <dd className="mt-0.5 text-lg font-semibold text-foreground">
            {(diagnosis.species_confidence * 100).toFixed(0)}%
          </dd>
        </div>
        <div className="rounded-xl border border-border bg-muted/50 px-3 py-2.5 text-center">
          <dt className="text-xs text-muted-foreground">증상 확신도</dt>
          <dd className="mt-0.5 text-lg font-semibold text-foreground">
            {(diagnosis.symptom_confidence * 100).toFixed(0)}%
          </dd>
        </div>
      </dl>

      {prescription ? (
        <p className="mt-4 rounded-xl bg-accent px-4 py-3 text-sm text-accent-foreground">
          {prescription}
        </p>
      ) : (
        <button
          type="button"
          onClick={() => void onGenerateCareGuide()}
          disabled={loading}
          className="mt-4 inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              처방 생성 중…
            </>
          ) : (
            "케어 처방 받기"
          )}
        </button>
      )}

      {error ? (
        <p className="mt-4 rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</p>
      ) : null}
    </div>
  );
}
