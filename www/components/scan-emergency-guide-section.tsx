"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, FileText } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { fetchEmergencyGuide, type EmergencyGuide, type EmergencyHotline, type EmergencyStep } from "@/lib/safeteen-api";

function ChecklistCard({ title, steps }: { title: string; steps: EmergencyStep[] }) {
  const [done, setDone] = useState<Record<number, boolean>>({});
  const doneCount = steps.filter((s) => done[s.order]).length;
  const pct = steps.length ? Math.round((doneCount / steps.length) * 100) : 0;

  return (
    <div className="rounded-[18px] border border-slate-200 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
      <div className="flex items-baseline gap-2">
        <div className="text-[15px] font-bold text-slate-900">{title}</div>
        <div className="ml-auto text-xs font-semibold text-slate-500">
          {doneCount}/{steps.length}
        </div>
      </div>
      <div className="mt-3 h-1 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full bg-indigo-600 transition-all" style={{ width: `${pct}%` }} />
      </div>
      <div className="mt-3 flex flex-col gap-0.5">
        {steps.map((step) => {
          const isDone = !!done[step.order];
          return (
            <button
              key={step.order}
              type="button"
              onClick={() => setDone((prev) => ({ ...prev, [step.order]: !prev[step.order] }))}
              className="flex items-start gap-[11px] rounded-[10px] px-2 py-2.5 text-left transition hover:bg-slate-50"
            >
              <span
                className={`mt-0.5 h-[18px] w-[18px] shrink-0 rounded-[6px] ${
                  isDone ? "bg-indigo-600" : "border-[1.5px] border-slate-300"
                }`}
              />
              <span className="text-[13.5px] leading-snug text-slate-700">
                <span className={isDone ? "text-slate-400 line-through" : "font-medium text-slate-800"}>
                  {step.title}
                </span>
                <span className="block text-xs text-slate-400">{step.description}</span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default function EmergencyGuideSection() {
  const router = useRouter();
  const [guide, setGuide] = useState<EmergencyGuide | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [callTarget, setCallTarget] = useState<EmergencyHotline | null>(null);

  useEffect(() => {
    fetchEmergencyGuide()
      .then(setGuide)
      .catch((e) => setError(e instanceof Error ? e.message : "가이드를 불러오지 못했습니다."));
  }, []);

  return (
    <div className="max-w-[840px] space-y-0">
      <h1 className="text-[28px] font-extrabold tracking-tight text-slate-900">비상 대응 가이드</h1>
      <p className="mt-2.5 text-[14.5px] leading-relaxed text-slate-600">
        이미 계좌나 명의를 넘겼다면 <b className="font-bold text-slate-900">지급정지가 가장 급합니다.</b> 아래
        순서대로 진행하세요.
      </p>

      {error && (
        <div className="mt-5 flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <AlertCircle className="h-4 w-4 shrink-0" aria-hidden />
          {error}
        </div>
      )}

      {!guide && !error && (
        <div className="mt-8 flex items-center gap-2 text-sm text-slate-500">
          <Spinner className="h-4 w-4" /> 대응 가이드를 불러오는 중…
        </div>
      )}

      {guide && (
        <>
          <div className="mt-[22px] grid grid-cols-1 gap-3 sm:grid-cols-3">
            {guide.hotlines.map((h) => (
              <button
                key={h.name}
                type="button"
                onClick={() => setCallTarget(h)}
                className="block rounded-2xl border border-slate-200 bg-white p-[18px] text-left shadow-[0_1px_2px_rgba(15,23,42,0.04)] transition hover:border-indigo-200 hover:bg-indigo-50/40"
              >
                <div className="text-[22px] font-extrabold tabular-nums tracking-tight text-indigo-600">
                  {h.phone_number}
                </div>
                <div className="mt-[5px] text-[13.5px] font-bold text-slate-900">{h.name}</div>
                <div className="mt-[5px] text-xs leading-relaxed text-slate-500">{h.description}</div>
              </button>
            ))}
          </div>

          <div className="mt-3.5 grid grid-cols-1 gap-3.5 sm:grid-cols-2">
            <ChecklistCard title="계좌 지급정지" steps={guide.account_freeze_steps} />
            <ChecklistCard title="경찰 신고" steps={guide.police_report_steps} />
          </div>

          <div className="mt-3.5 flex flex-wrap items-center gap-5 rounded-[18px] bg-slate-900 p-6 text-slate-200">
            <div className="min-w-[260px] flex-1">
              <div className="text-[11.5px] font-bold tracking-wider text-indigo-300">STEP 3 · 신고 서류 준비</div>
              <div className="mt-2 text-lg font-bold tracking-tight text-white">
                사건 경위서, 직접 쓰지 마세요
              </div>
              <div className="mt-1.5 max-w-[36em] text-[13.5px] leading-relaxed text-slate-300">
                피해 상황을 설명하면 AI가 경찰 제출용 진술서 문체로 정리해 드립니다. 증거 목록과 요청
                조치까지 함께 생성되어 그대로 출력해 제출할 수 있습니다.
              </div>
            </div>
            <button
              type="button"
              onClick={() => router.push("/scan/incident-report")}
              className="flex items-center gap-2 rounded-[11px] bg-indigo-600 px-[22px] py-[13px] text-sm font-bold text-white transition hover:bg-indigo-500"
            >
              <FileText className="h-4 w-4" aria-hidden />
              AI 경위서 작성하기
            </button>
          </div>
        </>
      )}

      <Dialog open={!!callTarget} onOpenChange={(open) => !open && setCallTarget(null)}>
        <DialogContent showCloseButton={false} className="max-w-[420px] gap-0 rounded-2xl p-[22px]">
          {callTarget && (
            <>
              <DialogTitle className="text-xs font-bold text-slate-500">전화를 연결할까요?</DialogTitle>
              <div className="mt-2 text-[30px] font-extrabold tabular-nums tracking-tight text-indigo-600">
                {callTarget.phone_number}
              </div>
              <div className="mt-1 text-sm font-bold text-slate-900">{callTarget.name}</div>
              <DialogDescription className="mt-1 text-[12.5px] leading-relaxed text-slate-500">
                {callTarget.description}
              </DialogDescription>
              <div className="mt-3.5 rounded-[10px] border border-slate-200 bg-slate-50 p-[11px] text-xs leading-relaxed text-slate-600">
                통화 전 계좌번호·송금 시각·상대방 아이디를 손에 들고 계시면 상담이 빨라집니다.
              </div>
              <div className="mt-[18px] flex gap-[9px]">
                <a
                  href={`tel:${callTarget.phone_number}`}
                  className="flex-1 rounded-[11px] bg-indigo-600 py-3 text-center text-[13.5px] font-bold text-white transition hover:bg-indigo-700"
                >
                  통화 연결
                </a>
                <button
                  type="button"
                  onClick={() => setCallTarget(null)}
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
