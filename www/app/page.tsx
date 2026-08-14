"use client";

import Link from "next/link";
import { ShieldAlert } from "lucide-react";
import GeminiChat from "@/components/gemini-chat";
import { Badge } from "@/components/ui/badge";
import ScanAppShell from "@/components/scan-app-shell";

const STEPS = [
  {
    no: "STEP 01",
    title: "광고를 붙여넣기",
    body: "문자·DM·구인글 캡처를 그대로 올리면 개인정보를 자동으로 가린 뒤 분석합니다.",
  },
  {
    no: "STEP 02",
    title: "위험도와 근거 확인",
    body: "은어 사전과 판례 데이터를 대조해 0~100 점수와 적용 법률을 제시합니다.",
  },
  {
    no: "STEP 03",
    title: "대안 또는 대응으로",
    body: "합법 정책자금을 연결하거나, 이미 당했다면 지급정지·신고 절차를 안내합니다.",
  },
];

const TREND_TERMS = ["내구제", "작업대출", "선입금", "휴대폰깡", "통장 대여", "신용카드 현금화"];

const SUGGESTIONS = ["내구제 대출이 뭐야?", "선입금을 요구하는 대출, 안전한가요?", "불법 사금융 피해를 당했을 때 어디에 신고하나요?"];

export default function Home() {
  return (
    <ScanAppShell maxWidthClassName="max-w-5xl">
      <div className="max-w-3xl">
        <div className="inline-flex items-center gap-[7px] rounded-full bg-indigo-50 px-[11px] py-[5px] text-xs font-semibold text-indigo-700">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-indigo-600" aria-hidden />
          AI 실시간 탐지 가동 중
        </div>
        <h1 className="mt-5 max-w-[16em] text-3xl font-extrabold leading-[1.25] tracking-tight text-slate-900 sm:text-[40px]">
          SNS에서 본 그 대출 광고,
          <br />
          안전한지 먼저 확인하세요.
        </h1>
        <p className="mt-4 max-w-[34em] text-[15.5px] leading-[1.7] text-slate-600">
          작업대출·내구제·대포통장 명의대여 같은 변종 불법금융을 AI가 진단합니다. 광고 문구를
          붙여넣거나 캡처를 올리면 위험도와 관련 법률, 그리고 이용할 수 있는 정부지원 자금을 함께
          알려드립니다.
        </p>

        <div className="mt-[26px] flex flex-wrap gap-2.5">
          <Link
            href="/scan"
            className="rounded-[11px] bg-indigo-600 px-[22px] py-[13px] text-[14.5px] font-bold text-white shadow-sm transition hover:bg-indigo-700"
          >
            지금 진단하기
          </Link>
          <Link
            href="/scan/guide"
            className="rounded-[11px] border border-slate-200 bg-white px-[22px] py-[13px] text-[14.5px] font-semibold text-slate-900 transition hover:border-slate-300 hover:bg-slate-50"
          >
            이미 피해를 입었어요
          </Link>
        </div>
      </div>

      <div className="mt-10 grid grid-cols-1 gap-3.5 sm:grid-cols-3">
        {STEPS.map((s) => (
          <div
            key={s.no}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]"
          >
            <div className="text-[11px] font-bold tracking-wider text-indigo-600">{s.no}</div>
            <div className="mt-2 text-[15px] font-bold tracking-tight text-slate-900">{s.title}</div>
            <div className="mt-1.5 text-[13px] leading-relaxed text-slate-500">{s.body}</div>
          </div>
        ))}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-[20px] border border-slate-200 bg-white p-[22px] shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
          <div className="flex items-center gap-[9px]">
            <span className="h-2 w-2 rounded-full bg-emerald-600" aria-hidden />
            <div className="text-[14.5px] font-bold text-slate-900">AI 상담 챗봇</div>
            <span className="text-[11.5px] text-slate-500">24시간 · 익명</span>
          </div>
          <div className="mt-4 space-y-2.5">
            <div className="max-w-[80%] rounded-[14px] rounded-bl-[4px] bg-slate-100 px-3.5 py-2.5 text-[13.5px] leading-relaxed text-slate-700">
              무엇이든 물어보세요. 상담 내용은 저장되지 않습니다.
            </div>
            <div className="flex flex-wrap justify-end gap-2">
              {SUGGESTIONS.map((s) => (
                <Badge
                  key={s}
                  variant="outline"
                  className="cursor-default rounded-full border-indigo-100 bg-indigo-50 px-3 py-1.5 text-xs font-normal text-indigo-800"
                >
                  {s}
                </Badge>
              ))}
            </div>
          </div>
          <div className="mt-4">
            <GeminiChat variant="apple" inputPlaceholder="질문을 입력하세요" />
          </div>
        </div>

        <div className="rounded-[20px] bg-slate-900 p-[22px] text-slate-200">
          <div className="text-xs font-bold tracking-wider text-indigo-300">이번 주 탐지 급증 은어</div>
          <div className="mt-3.5 flex flex-wrap gap-2">
            {TREND_TERMS.map((t) => (
              <span
                key={t}
                className="rounded-lg border border-white/10 bg-white/[0.08] px-2.5 py-1.5 text-[12.5px] font-semibold"
              >
                {t}
              </span>
            ))}
          </div>
          <div className="my-5 h-px bg-white/10" />
          <p className="text-[13px] leading-relaxed text-slate-300">
            &ldquo;휴대폰만 있으면 당일 현금&rdquo;은 <b className="text-white">내구제 대출</b>의
            대표적 문구입니다. 명의를 빌려주는 순간{" "}
            <b className="text-white">전자금융거래법 위반</b>으로 처벌 대상이 될 수 있습니다.
          </p>
          <Link
            href="/scan"
            className="mt-[18px] flex items-center justify-center gap-1.5 rounded-[10px] bg-indigo-600 py-[11px] text-[13.5px] font-bold text-white transition hover:bg-indigo-500"
          >
            <ShieldAlert className="h-4 w-4" aria-hidden />
            내가 본 광고 진단하기
          </Link>
        </div>
      </div>
    </ScanAppShell>
  );
}
