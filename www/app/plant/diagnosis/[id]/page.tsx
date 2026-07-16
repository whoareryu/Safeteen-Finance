"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import PlantDiagnosisResultCard from "@/components/plant-diagnosis-result-card";
import { fetchDiagnosis, type DiagnosisResult } from "@/lib/plant-api";

export default function PlantDiagnosisDetailPage() {
  const params = useParams<{ id: string }>();
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await fetchDiagnosis(Number(params.id));
        if (!cancelled) setDiagnosis(result);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "진단 결과를 불러오지 못했습니다.");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [params.id]);

  return (
    <div className="mx-auto max-w-2xl px-6 pb-28 pt-10">
      {error ? (
        <p className="rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</p>
      ) : diagnosis ? (
        <PlantDiagnosisResultCard diagnosis={diagnosis} />
      ) : (
        <p className="text-sm text-muted-foreground">불러오는 중…</p>
      )}
    </div>
  );
}
