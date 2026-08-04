"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { generateCareGuide, type DiagnosisResult } from "@/lib/plant-api";
import { translateSpecies, translateSymptom } from "@/lib/plant-labels";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

// 분류기 자체 확신도가 이 미만이면 결과를 단정적으로 보여주지 않고 재촬영을 안내한다.
const LOW_CONFIDENCE_THRESHOLD = 0.5;

export default function PlantDiagnosisResultCard({ diagnosis }: { diagnosis: DiagnosisResult }) {
  const [loading, setLoading] = useState(false);
  const [prescription, setPrescription] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  // symptom_confidence는 증상 미판정 상태(하우스플랜트 품종 전용 모델)에서 항상 0이 되므로
  // 게이팅에 쓰지 않는다 — 여기서 확신도가 실제로 낮은 건 품종 분류뿐이다.
  const isLowConfidence = diagnosis.species_confidence < LOW_CONFIDENCE_THRESHOLD;

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
        <Badge className="rounded-full bg-accent px-3 py-1 text-sm font-semibold text-accent-foreground hover:bg-accent">
          {translateSpecies(diagnosis.detected_species)}
        </Badge>
        <Badge
          variant="secondary"
          className="rounded-full px-3 py-1 text-sm font-medium hover:bg-secondary"
        >
          {translateSymptom(diagnosis.symptom_label)}
        </Badge>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-3">
        <div
          className={`rounded-xl border px-3 py-2.5 text-center ${
            isLowConfidence
              ? "border-destructive/40 bg-destructive/10"
              : "border-border bg-muted/50"
          }`}
        >
          <dt className="text-xs text-muted-foreground">품종 확신도</dt>
          <dd className="mt-0.5 text-lg font-semibold text-foreground">
            {(diagnosis.species_confidence * 100).toFixed(0)}%
          </dd>
        </div>
        <div
          className={`rounded-xl border px-3 py-2.5 text-center ${
            isLowConfidence
              ? "border-destructive/40 bg-destructive/10"
              : "border-border bg-muted/50"
          }`}
        >
          <dt className="text-xs text-muted-foreground">증상 확신도</dt>
          <dd className="mt-0.5 text-lg font-semibold text-foreground">
            {(diagnosis.symptom_confidence * 100).toFixed(0)}%
          </dd>
        </div>
      </dl>

      {isLowConfidence ? (
        <p className="mt-3 rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive">
          확신도가 낮아요. 잎 전체가 잘 보이도록 밝은 곳에서 사진을 다시 찍어보시면 더 정확해요.
        </p>
      ) : null}

      {prescription ? (
        <p className="mt-4 rounded-xl bg-accent px-4 py-3 text-sm text-accent-foreground">
          {prescription}
        </p>
      ) : (
        <Button
          type="button"
          onClick={() => void onGenerateCareGuide()}
          disabled={loading}
          className="mt-4 rounded-full px-5"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              처방 생성 중…
            </>
          ) : (
            "케어 처방 받기"
          )}
        </Button>
      )}

      {error ? (
        <p className="mt-4 rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</p>
      ) : null}
    </div>
  );
}
