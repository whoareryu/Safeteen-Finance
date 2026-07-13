"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { generateCareGuide, type DiagnosisResult } from "@/lib/plant-api";

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
    <div className="plant-diagnosis-result-card w-full max-w-none rounded-2xl border border-black/[0.08] bg-white p-6">
      <img
        src={diagnosis.photo_url}
        alt="진단한 잎사귀 사진"
        className="max-h-60 w-full rounded-lg object-contain"
      />

      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <dt className="text-[#86868b]">품종</dt>
          <dd className="font-medium text-[#1d1d1f]">{diagnosis.detected_species}</dd>
        </div>
        <div>
          <dt className="text-[#86868b]">증상</dt>
          <dd className="font-medium text-[#1d1d1f]">{diagnosis.symptom_label}</dd>
        </div>
        <div>
          <dt className="text-[#86868b]">품종 확신도</dt>
          <dd>{(diagnosis.species_confidence * 100).toFixed(0)}%</dd>
        </div>
        <div>
          <dt className="text-[#86868b]">증상 확신도</dt>
          <dd>{(diagnosis.symptom_confidence * 100).toFixed(0)}%</dd>
        </div>
      </dl>

      {prescription ? (
        <p className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          {prescription}
        </p>
      ) : (
        <button
          type="button"
          onClick={() => void onGenerateCareGuide()}
          disabled={loading}
          className="apple-cta-primary mt-4 inline-flex items-center gap-2 rounded-full px-5 py-2 text-sm disabled:opacity-50"
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

      {error ? <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}
    </div>
  );
}
