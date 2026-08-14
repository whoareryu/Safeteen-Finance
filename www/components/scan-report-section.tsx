"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FileText, Gavel, ScanSearch } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { useScanResult } from "@/components/scan-result-context";
import type { RiskLevel } from "@/lib/safeteen-api";

const RISK_STYLE: Record<RiskLevel, { label: string; banner: string; ring: string }> = {
  DANGER: { label: "DANGER · 위험", banner: "bg-rose-600", ring: "text-rose-600" },
  WARNING: { label: "WARNING · 경고", banner: "bg-amber-500", ring: "text-amber-600" },
  SAFE: { label: "SAFE · 안전", banner: "bg-emerald-600", ring: "text-emerald-600" },
};

export default function ReportSection() {
  const router = useRouter();
  const { result, justScanned, consumeJustScanned } = useScanResult();
  const [showDanger, setShowDanger] = useState(false);

  useEffect(() => {
    if (justScanned && result?.risk_level === "DANGER") {
      setShowDanger(true);
    }
    if (justScanned) consumeJustScanned();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!result) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <ScanSearch className="h-8 w-8 text-slate-300" aria-hidden />
        <p className="text-sm font-medium text-slate-700">아직 진단 결과가 없어요</p>
        <p className="text-sm text-slate-500">AI 스캐너에서 광고 문구나 이미지를 먼저 진단해 주세요.</p>
        <Link
          href="/scan"
          className="mt-2 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700"
        >
          AI 스캐너로 이동
        </Link>
      </div>
    );
  }

  const style = RISK_STYLE[result.risk_level];
  const scoreBars = Array.from({ length: 10 }, (_, i) => i < Math.round(result.risk_score / 10));

  return (
    <div className="max-w-[840px] space-y-0">
      <div className="text-[12.5px] font-semibold text-slate-500">진단 결과</div>

      <div className="mt-2.5 overflow-hidden rounded-[20px] border border-slate-200 bg-white shadow-[0_1px_3px_rgba(15,23,42,0.06)]">
        <div className={`${style.banner} px-[26px] py-[24px] text-white`}>
          <div className="flex flex-wrap items-start gap-5">
            <div>
              <div className="inline-block rounded-[6px] bg-white/20 px-2.5 py-1 text-xs font-extrabold tracking-wider">
                {style.label}
              </div>
              <div className="mt-3 text-[26px] font-extrabold tracking-tight">{result.crime_type}</div>
              <div className="mt-1.5 max-w-[32em] text-[13.5px] leading-relaxed text-white/85">
                {result.risk_level === "DANGER"
                  ? "즉시 연락을 중단하고, 신분증·통장·계좌 정보를 절대 전달하지 마세요."
                  : result.risk_level === "WARNING"
                    ? "조건을 다시 확인하고, 선입금이나 개인정보 요구가 있다면 응하지 마세요."
                    : "제도권 금융 상품으로 보이지만, 최종 계약 전 공식 채널에서 다시 한번 확인하세요."}
              </div>
            </div>
            <div className="ml-auto text-right">
              <div className="text-[11.5px] font-bold tracking-wider text-white/75">RISK SCORE</div>
              <div className="text-[52px] font-extrabold leading-none tracking-tight">{result.risk_score}</div>
              <div className="mt-2 flex justify-end gap-[3px]">
                {scoreBars.map((filled, i) => (
                  <span
                    key={i}
                    className={`h-[6px] w-[9px] rounded-sm ${filled ? "bg-white/85" : "bg-white/30"}`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="px-[26px] py-6">
          <div className="text-[12.5px] font-bold text-slate-500">감지된 불법 은어</div>
          <div className="mt-2.5 flex flex-wrap gap-2">
            {result.detected_terms.length === 0 ? (
              <p className="text-sm text-slate-400">감지된 은어가 없어요.</p>
            ) : (
              result.detected_terms.map((term) => (
                <Badge
                  key={term}
                  variant="outline"
                  className="rounded-[8px] border-rose-200 bg-rose-50 px-[11px] py-1.5 text-[12.5px] font-semibold text-rose-800"
                >
                  {term}
                </Badge>
              ))
            )}
          </div>

          <div className="mt-6 rounded-[14px] border border-slate-200 p-[18px]">
            <div className="flex items-center gap-2 text-[13.5px] font-bold text-slate-900">
              <FileText className="h-4 w-4 text-indigo-600" aria-hidden />
              팩트체크
            </div>
            <div className="mt-2 text-[13.5px] leading-[1.75] text-slate-600">{result.fact_check_summary}</div>
          </div>

          {result.legal_warning && (
            <div className="mt-3 rounded-[14px] border border-orange-200 bg-amber-50 p-[18px]">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-sm bg-amber-500" aria-hidden />
                <div className="text-[13.5px] font-bold text-amber-800">
                  <Gavel className="mr-1 inline h-3.5 w-3.5" aria-hidden />
                  법률 경고
                </div>
              </div>
              <div className="mt-2 text-[13.5px] leading-[1.75] text-amber-900">{result.legal_warning}</div>
            </div>
          )}

          {result.alternative_policy && (
            <div className="mt-3 flex flex-wrap items-center gap-4 rounded-[14px] border border-emerald-200 bg-emerald-50 p-[18px]">
              <div className="min-w-[240px] flex-1">
                <div className="text-xs font-bold tracking-wide text-emerald-700">합법 대안 정책 매칭</div>
                <div className="mt-1.5 text-[15px] font-bold text-emerald-950">
                  {result.alternative_policy.title}
                </div>
                <div className="mt-1 text-[13px] leading-relaxed text-emerald-800">
                  {result.alternative_policy.description}
                </div>
              </div>
              <button
                type="button"
                onClick={() => router.push("/scan/policy")}
                className="rounded-[10px] bg-emerald-600 px-[18px] py-[11px] text-[13.5px] font-bold text-white transition hover:bg-emerald-700"
              >
                대안 자금 보기
              </button>
            </div>
          )}

          <div className="mt-[22px] flex flex-wrap items-center gap-2.5 border-t border-slate-100 pt-5">
            <Link
              href="/scan/guide"
              className="rounded-[11px] bg-rose-600 px-[22px] py-[13px] text-sm font-bold text-white transition hover:bg-rose-700"
            >
              지금 바로 대응 가이드 보기
            </Link>
            <Link
              href="/scan"
              className="rounded-[11px] border border-slate-200 px-5 py-[13px] text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
            >
              다른 광고 진단하기
            </Link>
            <div className="ml-auto text-xs text-slate-400">AI 진단은 법률 자문이 아닙니다</div>
          </div>
        </div>
      </div>

      <Dialog open={showDanger} onOpenChange={setShowDanger}>
        <DialogContent showCloseButton={false} className="max-w-[440px] gap-0 overflow-hidden rounded-2xl p-0">
          <div className="bg-rose-600 px-[22px] py-5 text-white">
            <div className="text-[11.5px] font-extrabold tracking-wider">DANGER · 위험도 {result.risk_score}</div>
            <DialogTitle className="mt-1.5 text-[19px] font-extrabold tracking-tight text-white">
              지금 연락을 중단하세요
            </DialogTitle>
          </div>
          <div className="px-[22px] py-5">
            <DialogDescription className="text-[13.5px] leading-relaxed text-slate-700">
              {result.crime_type}(으)로 판단됩니다. 리포트를 읽기 전에 아래 세 가지를 먼저 지켜주세요.
            </DialogDescription>
            <div className="mt-3.5 flex flex-col gap-2.5">
              {[
                "신분증·통장·계좌 사진을 전달하지 않기",
                "대화 내용을 삭제하지 말고 캡처로 보관하기",
                "이미 전달했다면 즉시 지급정지 신청하기",
              ].map((step, i) => (
                <div key={step} className="flex gap-2.5 text-[13px] text-slate-900">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-rose-50 text-[11px] font-extrabold text-rose-700">
                    {i + 1}
                  </span>
                  {step}
                </div>
              ))}
            </div>
            <div className="mt-5 flex gap-2.5">
              <button
                type="button"
                onClick={() => {
                  setShowDanger(false);
                  router.push("/scan/guide");
                }}
                className="flex-1 rounded-[11px] bg-rose-600 py-3 text-center text-[13.5px] font-bold text-white transition hover:bg-rose-700"
              >
                대응 가이드 열기
              </button>
              <button
                type="button"
                onClick={() => setShowDanger(false)}
                className="rounded-[11px] border border-slate-200 px-4 py-3 text-[13.5px] font-semibold text-slate-600 hover:bg-slate-50"
              >
                리포트 보기
              </button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
