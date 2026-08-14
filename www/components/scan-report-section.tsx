"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AlertTriangle, ExternalLink, FileText, Gavel, Landmark, ScanSearch, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { RiskLevel } from "@/lib/safeteen-api";
import { useScanResult } from "@/components/scan-result-context";

const RISK_STYLE: Record<RiskLevel, { label: string; badge: string; ring: string; bar: string }> = {
  DANGER: {
    label: "위험 DANGER",
    badge: "border-transparent bg-rose-600 text-white shadow-[0_0_20px_-4px_rgba(225,29,72,0.6)]",
    ring: "text-rose-600",
    bar: "[&>div]:bg-rose-600",
  },
  WARNING: {
    label: "경고 WARNING",
    badge: "border-transparent bg-amber-500 text-white shadow-[0_0_20px_-4px_rgba(245,158,11,0.6)]",
    ring: "text-amber-500",
    bar: "[&>div]:bg-amber-500",
  },
  SAFE: {
    label: "안전 SAFE",
    badge: "border-transparent bg-emerald-600 text-white shadow-[0_0_20px_-4px_rgba(5,150,105,0.6)]",
    ring: "text-emerald-600",
    bar: "[&>div]:bg-emerald-600",
  },
};

export default function ReportSection() {
  const { result } = useScanResult();
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    if (!result) return;
    setAnimatedScore(0);
    const id = requestAnimationFrame(() => setAnimatedScore(result.risk_score));
    return () => cancelAnimationFrame(id);
  }, [result]);

  if (!result) {
    return (
      <Card className="border-slate-200 shadow-sm">
        <CardContent className="flex flex-col items-center gap-3 py-16 text-center">
          <ScanSearch className="h-8 w-8 text-slate-300" aria-hidden />
          <p className="text-sm font-medium text-slate-700">아직 진단 결과가 없어요</p>
          <p className="text-sm text-slate-500">AI 스캐너에서 광고 문구나 이미지를 먼저 진단해 주세요.</p>
          <Link
            href="/scan"
            className="mt-2 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700"
          >
            AI 스캐너로 이동
          </Link>
        </CardContent>
      </Card>
    );
  }

  const style = RISK_STYLE[result.risk_level];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900 sm:text-2xl">AI 위험 진단 리포트</h1>
        <p className="mt-1 text-sm text-slate-500">방금 진단한 내용의 분석 결과예요.</p>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardContent className="flex flex-col items-center gap-4 py-8 text-center sm:flex-row sm:items-center sm:justify-between sm:text-left">
          <div className="space-y-3">
            <Badge className={`rounded-full px-3 py-1 text-sm font-semibold ${style.badge}`}>
              <ShieldAlert className="h-3.5 w-3.5" aria-hidden />
              {style.label}
            </Badge>
            <p className="text-sm font-medium text-slate-700">{result.crime_type}</p>
          </div>

          <div className="flex flex-col items-center gap-2 sm:items-end">
            <span className={`text-4xl font-bold tabular-nums ${style.ring}`}>{result.risk_score}</span>
            <Progress value={animatedScore} className={`h-2 w-40 duration-700 ${style.bar}`} />
            <span className="text-xs text-slate-400">위험도 점수 (0~100)</span>
          </div>
        </CardContent>
      </Card>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">감지된 불법 은어</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {result.detected_terms.length === 0 ? (
            <p className="text-sm text-slate-400">감지된 은어가 없어요.</p>
          ) : (
            result.detected_terms.map((term) => (
              <Badge
                key={term}
                variant="outline"
                className="rounded-full border-rose-200 bg-rose-50 px-3 py-1 text-rose-700"
              >
                #{term}
              </Badge>
            ))
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card className="border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <FileText className="h-4 w-4 text-indigo-600" aria-hidden />
              AI 팩트체크 요약
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-slate-600">{result.fact_check_summary}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Gavel className="h-4 w-4 text-rose-600" aria-hidden />
              법적 처벌 및 신용 불이익 경고
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 rounded-lg border border-rose-100 bg-rose-50 p-3">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" aria-hidden />
              <p className="text-sm leading-relaxed text-rose-700">{result.legal_warning}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {result.alternative_policy ? (
        <Card className="border-indigo-200 bg-indigo-50/50 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Landmark className="h-4 w-4 text-indigo-600" aria-hidden />
              대신 이용할 수 있는 합법 대안
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-800">{result.alternative_policy.title}</p>
              <p className="mt-0.5 text-sm text-slate-600">{result.alternative_policy.description}</p>
            </div>
            <a
              href={result.alternative_policy.official_link}
              target="_blank"
              rel="noreferrer"
              className="inline-flex shrink-0 items-center justify-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-slate-700"
            >
              공식 홈페이지 신청하기
              <ExternalLink className="h-3.5 w-3.5" aria-hidden />
            </a>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
