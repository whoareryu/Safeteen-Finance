"use client";

import Link from "next/link";
import GeminiChat from "@/components/gemini-chat";
import { uploadPlantPhoto } from "@/lib/plant-api";

const DEFAULT_REGION = "서울";

async function diagnoseFromChat(file: File): Promise<string> {
  const diagnosis = await uploadPlantPhoto(file, DEFAULT_REGION);
  const speciesPct = (diagnosis.species_confidence * 100).toFixed(0);
  const symptomPct = (diagnosis.symptom_confidence * 100).toFixed(0);
  return [
    `🌱 진단 결과: ${diagnosis.detected_species} (신뢰도 ${speciesPct}%)`,
    `증상: ${diagnosis.symptom_label} (신뢰도 ${symptomPct}%)`,
    "",
    "케어 방법이 궁금하면 이어서 물어보세요!",
  ].join("\n");
}

export default function Home() {
  return (
    <main className="home-main min-h-[calc(100dvh-var(--site-header-height))]">
      <section className="mx-auto max-w-2xl px-6 py-10 text-center">
        <p className="text-sm font-medium text-primary">새싹</p>
        <h1 className="mt-2 text-3xl font-semibold text-foreground">
          새싹과 함께하는 반려식물 케어
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          궁금한 걸 물어보거나 잎사귀 사진을 올려보세요. 품종·증상 진단부터 날씨 기반 물주기
          알림까지, AI 에이전트가 초보 식집사를 도와드려요.
        </p>
        <Link
          href="/plant/care-calendar"
          className="mt-4 inline-block text-sm text-primary underline underline-offset-4"
        >
          내 식물 케어 일정 보기 →
        </Link>
      </section>

      <section className="mx-auto max-w-2xl px-6 pb-10">
        <GeminiChat
          variant="apple"
          apiPath="/api/plant/chat"
          model="exaone3.5:2.4b"
          inputPlaceholder="새싹이에게 물어보기"
          onImageAttach={diagnoseFromChat}
        />
      </section>
    </main>
  );
}
