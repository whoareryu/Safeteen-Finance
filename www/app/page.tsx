"use client";

import Link from "next/link";
import { CalendarCheck, Leaf, Sparkles } from "lucide-react";
import GeminiChat from "@/components/gemini-chat";
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
      <section className="saessak-photo-hero relative overflow-hidden px-6 pb-28 pt-14 text-center sm:pb-36 sm:pt-20">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="https://images.unsplash.com/photo-1755504980103-374cf009b201?w=1600&q=80&auto=format&fit=crop"
          alt=""
          aria-hidden
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="saessak-photo-scrim absolute inset-0" aria-hidden />

        <div className="relative mx-auto max-w-2xl">
          <div className="saessak-glass-card mx-auto inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium text-white shadow-sm">
            <Leaf className="h-4 w-4" aria-hidden />
            새싹
          </div>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            새싹과 함께하는 반려식물 케어
          </h1>
          <p className="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-white/85 sm:text-base">
            궁금한 걸 물어보거나 잎사귀 사진을 올려보세요. 품종·증상 진단부터 날씨 기반 물주기
            알림까지, AI 에이전트가 초보 식집사를 도와드려요.
          </p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/plant/care-calendar"
              className="saessak-glass-card inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:shadow-md"
            >
              <CalendarCheck className="h-4 w-4" aria-hidden />
              내 식물 케어 일정 보기
            </Link>
          </div>
        </div>
      </section>

      {/* 히어로 아래로 겹치게 끌어올린 유리 패널 — 채팅을 화면 중앙부의 주인공으로 배치 */}
      <section className="home-content-layer relative z-10 mx-auto -mt-16 max-w-2xl px-6 sm:-mt-20">
        <div className="saessak-glass-panel rounded-3xl p-4 sm:p-6">
          <h2 className="text-center text-base font-semibold text-foreground sm:text-lg">
            새싹에게 물어보세요
          </h2>
          <div className="mt-3 flex flex-wrap justify-center gap-2">
            {SUGGESTIONS.map((s) => (
              <span
                key={s}
                className="rounded-full border border-border bg-background/70 px-3 py-1.5 text-xs text-muted-foreground"
              >
                {s}
              </span>
            ))}
          </div>
          <div className="mt-4">
            <GeminiChat
              variant="apple"
              apiPath="/api/plant/chat"
              model="exaone3.5:2.4b"
              inputPlaceholder="새싹이에게 물어보기"
              onImageAttach={diagnoseFromChat}
            />
          </div>
        </div>
      </section>

      <section className="saessak-hero-bg px-6 pb-28 pt-12">
        <div className="mx-auto grid max-w-3xl gap-4 sm:grid-cols-3">
          {FEATURES.map(({ href, Icon, title, description }) => (
            <Link key={href} href={href}>
              <Card className="saessak-card h-full border-0 transition hover:-translate-y-0.5 hover:shadow-lg">
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
    </main>
  );
}
