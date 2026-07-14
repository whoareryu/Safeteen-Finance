"use client";

import Link from "next/link";
import { CalendarCheck, Leaf, Sparkles } from "lucide-react";
import GeminiChat from "@/components/gemini-chat";
import WeatherWidget from "@/components/weather-widget";
import { Card, CardContent, CardTitle, CardDescription } from "@/components/ui/card";
import { uploadPlantPhoto } from "@/lib/plant-api";

const DEFAULT_REGION = "서울";

const FEATURES = [
  {
    href: "/plant",
    Icon: Leaf,
    title: "AI 잎사귀 진단",
    description: "사진 한 장으로 품종과 병징을 진단해요.",
  },
  {
    href: "/plant/care-calendar",
    Icon: CalendarCheck,
    title: "케어 캘린더",
    description: "물주기·시비 일정을 자동으로 챙겨드려요.",
  },
  {
    href: "/social",
    Icon: Sparkles,
    title: "식집사 커뮤니티",
    description: "다른 식집사들과 케어 팁을 나눠보세요.",
  },
] as const;

const SUGGESTIONS = ["몬스테라 물 주기 주기가 어떻게 돼?", "잎이 노랗게 변했어, 왜 그럴까?", "초보자에게 좋은 식물 추천해줘"];

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
      <section className="saessak-hero-bg relative overflow-hidden px-6 pb-16 pt-14 text-center sm:pt-20">
        <div className="mx-auto max-w-2xl">
          <div className="saessak-glass-card mx-auto inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium text-primary shadow-sm">
            <Leaf className="h-4 w-4" aria-hidden />
            새싹
          </div>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            새싹과 함께하는 반려식물 케어
          </h1>
          <p className="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-muted-foreground sm:text-base">
            궁금한 걸 물어보거나 잎사귀 사진을 올려보세요. 품종·증상 진단부터 날씨 기반 물주기
            알림까지, AI 에이전트가 초보 식집사를 도와드려요.
          </p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <div className="saessak-glass-card rounded-full px-2 py-1 shadow-sm">
              <WeatherWidget />
            </div>
            <Link
              href="/plant/care-calendar"
              className="saessak-glass-card inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium text-foreground shadow-sm transition hover:shadow-md"
            >
              <CalendarCheck className="h-4 w-4 text-primary" aria-hidden />
              내 식물 케어 일정 보기
            </Link>
          </div>
        </div>

        <div className="mx-auto mt-10 grid max-w-3xl gap-4 sm:grid-cols-3">
          {FEATURES.map(({ href, Icon, title, description }) => (
            <Link key={href} href={href}>
              <Card className="h-full border-border/70 bg-card/90 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
                <CardContent className="flex flex-col items-center gap-2 text-center">
                  <span className="flex h-11 w-11 items-center justify-center rounded-full bg-accent text-primary">
                    <Icon className="h-5 w-5" aria-hidden />
                  </span>
                  <CardTitle className="text-base">{title}</CardTitle>
                  <CardDescription>{description}</CardDescription>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      <section className="home-content-layer mx-auto max-w-2xl px-6 pb-16 pt-4">
        <h2 className="text-center text-lg font-semibold text-foreground">새싹에게 물어보세요</h2>
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {SUGGESTIONS.map((s) => (
            <span
              key={s}
              className="rounded-full border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground shadow-sm"
            >
              {s}
            </span>
          ))}
        </div>
        <div className="mt-6">
          <GeminiChat
            variant="apple"
            apiPath="/api/plant/chat"
            model="exaone3.5:2.4b"
            inputPlaceholder="새싹이에게 물어보기"
            onImageAttach={diagnoseFromChat}
          />
        </div>
      </section>
    </main>
  );
}
