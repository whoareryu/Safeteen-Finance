"use client";

import Link from "next/link";
import { FileSearch, ShieldAlert } from "lucide-react";
import GeminiChat from "@/components/gemini-chat";
import { Card, CardContent, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const FEATURES = [
  {
    href: "/scan",
    Icon: ShieldAlert,
    title: "AI 위험도 진단",
    description: "SNS 대출 광고 텍스트/이미지를 분석해 위험 등급을 알려드려요.",
  },
  {
    href: "/scan",
    Icon: FileSearch,
    title: "합법 대안 자금 안내",
    description: "불법 대출 대신 이용할 수 있는 정부 지원 청년 금융을 찾아드려요.",
  },
] as const;

const SUGGESTIONS = ["내구제 대출이 뭐야?", "선입금을 요구하는 대출, 안전한가요?", "불법 사금융 피해를 당했을 때 어디에 신고하나요?"];

export default function Home() {
  return (
    <main className="home-main min-h-[calc(100dvh-var(--site-header-height))]">
      <section className="photo-hero relative overflow-hidden px-6 pb-16 pt-14 text-center sm:pb-20 sm:pt-20">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="https://images.unsplash.com/photo-1755504980103-374cf009b201?w=1600&q=80&auto=format&fit=crop"
          alt=""
          aria-hidden
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="photo-scrim absolute inset-0" aria-hidden />

        <div className="relative mx-auto max-w-2xl">
          <div className="glass-card mx-auto inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium text-white shadow-sm">
            <ShieldAlert className="h-4 w-4" aria-hidden />
            SafeTeen Finance
          </div>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            SNS 불법 금융 광고, AI가 먼저 확인해드려요
          </h1>
          <p className="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-white/85 sm:text-base">
            인스타그램·텔레그램에서 본 대출·구인 광고가 의심스럽다면 텍스트나 캡처 이미지를
            올려보세요. AI가 위험도를 진단하고, 안전한 합법 금융 대안까지 안내해 드려요.
          </p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/scan"
              className="glass-card inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:shadow-md"
            >
              <ShieldAlert className="h-4 w-4" aria-hidden />
              지금 바로 위험도 진단하기
            </Link>
          </div>
        </div>
      </section>

      {/* 히어로 아래부터는 하나의 그라데이션 배경을 공유 — 채팅 유리 패널 뒤부터
          기능 카드 섹션까지 끊기지 않고 이어진다 */}
      <div className="hero-bg">
        {/* 히어로와 겹치지 않게, 화면 중앙부에 채팅을 배치 */}
        <section className="home-content-layer relative z-10 mx-auto max-w-2xl px-6 pt-8 sm:pt-10">
          <div className="glass-panel rounded-3xl p-4 sm:p-6">
            <h2 className="text-center text-base font-semibold text-foreground sm:text-lg">
              AI에게 물어보세요
            </h2>
            <div className="mt-3 flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <Badge
                  key={s}
                  variant="outline"
                  className="rounded-full border-border bg-background/70 px-3 py-1.5 text-xs font-normal text-muted-foreground"
                >
                  {s}
                </Badge>
              ))}
            </div>
            <div className="mt-4">
              <GeminiChat variant="apple" inputPlaceholder="궁금한 걸 물어보세요" />
            </div>
          </div>
        </section>

        <section className="px-6 pb-28 pt-12">
          <div className="mx-auto grid max-w-3xl gap-4 sm:grid-cols-2">
            {FEATURES.map(({ href, Icon, title, description }) => (
              <Link key={title} href={href}>
                <Card className="content-card h-full border-0 transition hover:-translate-y-0.5 hover:shadow-lg">
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
      </div>
    </main>
  );
}
