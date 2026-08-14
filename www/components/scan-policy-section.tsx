"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Landmark } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { useScanResult } from "@/components/scan-result-context";
import { listPolicies, type AlternativePolicy } from "@/lib/safeteen-api";

export default function PolicySection() {
  const { result } = useScanResult();
  const [policies, setPolicies] = useState<AlternativePolicy[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [leaveTarget, setLeaveTarget] = useState<AlternativePolicy | null>(null);

  useEffect(() => {
    listPolicies()
      .then(setPolicies)
      .catch((e) => setError(e instanceof Error ? e.message : "정책 목록을 불러오지 못했습니다."));
  }, []);

  const matched = result?.alternative_policy ?? null;
  const rest = (policies ?? []).filter((p) => p.title !== matched?.title);

  return (
    <div className="max-w-[840px] space-y-0">
      <h1 className="text-[28px] font-extrabold tracking-tight text-slate-900">정부지원 대안 자금</h1>
      <p className="mt-2.5 text-[14.5px] leading-relaxed text-slate-600">
        불법 사금융보다 먼저 확인해야 할 합법 청년 금융 지원입니다. 진단 결과와 매칭된 정책을 상단에
        표시합니다.
      </p>

      {error && (
        <div className="mt-5 flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <AlertCircle className="h-4 w-4 shrink-0" aria-hidden />
          {error}
        </div>
      )}

      {!policies && !error && (
        <div className="mt-8 flex items-center gap-2 text-sm text-slate-500">
          <Spinner className="h-4 w-4" /> 정책 목록을 불러오는 중…
        </div>
      )}

      {matched && (
        <div className="mt-[22px] rounded-[20px] border-[1.5px] border-indigo-600 bg-white p-6 shadow-[0_4px_14px_rgba(79,70,229,0.1)]">
          <div className="inline-block rounded-[6px] bg-indigo-600 px-[9px] py-1 text-[11px] font-extrabold tracking-wide text-white">
            진단 결과 매칭
          </div>
          <div className="mt-3 text-[21px] font-extrabold tracking-tight text-slate-900">{matched.title}</div>
          <div className="mt-2 max-w-[44em] text-sm leading-relaxed text-slate-600">{matched.description}</div>
          <div className="mt-4 flex flex-wrap items-center gap-4 border-t border-slate-100 pt-4">
            <button
              type="button"
              onClick={() => setLeaveTarget(matched)}
              className="ml-auto rounded-[10px] bg-indigo-600 px-[18px] py-[11px] text-[13.5px] font-bold text-white transition hover:bg-indigo-700"
            >
              공식 사이트에서 신청
            </button>
          </div>
        </div>
      )}

      {policies && (
        <div className="mt-3.5 grid grid-cols-1 gap-3.5 sm:grid-cols-2">
          {(matched ? rest : policies).map((p) => (
            <div
              key={p.title}
              className="flex flex-col rounded-[18px] border border-slate-200 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
                <Landmark className="h-[18px] w-[18px]" aria-hidden />
              </div>
              <div className="mt-[7px] text-base font-bold tracking-tight text-slate-900">{p.title}</div>
              <div className="mt-[7px] flex-1 text-[13px] leading-relaxed text-slate-500">{p.description}</div>
              <button
                type="button"
                onClick={() => setLeaveTarget(p)}
                className="mt-4 self-start rounded-[9px] border border-slate-200 px-[15px] py-[9px] text-[13px] font-semibold text-slate-900 transition hover:border-slate-300 hover:bg-slate-50"
              >
                자세히 보기
              </button>
            </div>
          ))}
        </div>
      )}

      <Dialog open={!!leaveTarget} onOpenChange={(open) => !open && setLeaveTarget(null)}>
        <DialogContent showCloseButton={false} className="max-w-[420px] gap-0 rounded-2xl p-[22px]">
          {leaveTarget && (
            <>
              <DialogTitle className="text-[16.5px] font-extrabold tracking-tight text-slate-900">
                공식 사이트로 이동합니다
              </DialogTitle>
              <DialogDescription className="mt-2 text-[13px] leading-relaxed text-slate-600">
                신청은 아래 도메인에서만 진행하세요. 비슷한 이름의 사이트에서 수수료·선입금을 요구하면
                사칭입니다.
              </DialogDescription>
              <div className="mt-3.5 rounded-xl border border-slate-200 p-[14px]">
                <div className="text-[15px] font-bold text-slate-900">{leaveTarget.title}</div>
                <div className="mt-2 font-mono text-[12.5px] text-indigo-600">
                  {leaveTarget.official_link.replace(/^https?:\/\//, "")}
                </div>
              </div>
              <div className="mt-[18px] flex gap-[9px]">
                <a
                  href={leaveTarget.official_link}
                  target="_blank"
                  rel="noreferrer"
                  className="flex-1 rounded-[11px] bg-indigo-600 py-3 text-center text-[13.5px] font-bold text-white transition hover:bg-indigo-700"
                >
                  이동하기
                </a>
                <button
                  type="button"
                  onClick={() => setLeaveTarget(null)}
                  className="rounded-[11px] border border-slate-200 px-4 py-3 text-[13.5px] font-semibold text-slate-600 hover:bg-slate-50"
                >
                  닫기
                </button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
