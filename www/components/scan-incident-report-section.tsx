"use client";

import { useEffect, useRef, useState } from "react";
import { AlertCircle, UploadCloud, X } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Spinner } from "@/components/ui/spinner";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { generateIncidentReport, type IncidentReportResult } from "@/lib/safeteen-api";
import { useScanToast } from "@/components/scan-toast";

type Section = { key: string; title: string; body: string };

function toSections(r: IncidentReportResult): Section[] {
  return [
    { key: "INCIDENT SUMMARY", title: "사건 개요", body: r.incident_summary },
    { key: "VICTIM STATEMENT", title: "피해자 진술서", body: r.victim_statement },
    { key: "EVIDENCE LIST", title: "제출 증거 목록", body: r.evidence_list.map((e, i) => `${i + 1}. ${e}`).join("\n") },
    { key: "REQUESTED ACTION", title: "경찰 요청 조치", body: r.requested_action },
  ];
}

export default function IncidentReportSection() {
  const { notify } = useScanToast();
  const [situation, setSituation] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IncidentReportResult | null>(null);
  const [copied, setCopied] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  function handleFile(selected: File | undefined) {
    if (!selected) return;
    setFile(selected);
    setPreviewUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return URL.createObjectURL(selected);
    });
  }

  function clearFile() {
    setFile(null);
    setPreviewUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function handleGenerateClick() {
    if (!situation.trim()) {
      notify("피해 상황을 먼저 입력해 주세요.");
      return;
    }
    setConfirmOpen(true);
  }

  async function confirmGenerate() {
    setConfirmOpen(false);
    setGenerating(true);
    setError(null);
    try {
      const r = await generateIncidentReport({ situation: situation.trim(), file });
      setResult(r);
      notify("경위서 초안이 생성되었습니다.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "경위서 생성 중 오류가 발생했습니다.");
    } finally {
      setGenerating(false);
    }
  }

  async function copyAll() {
    if (!result) return;
    const text = toSections(result)
      .map((s) => `[${s.title}]\n${s.body}`)
      .join("\n\n");
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      notify("경위서 전문이 클립보드에 복사되었습니다.");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      notify("복사에 실패했습니다. 텍스트를 직접 선택해 복사해 주세요.");
    }
  }

  return (
    <div className="max-w-[840px] space-y-0">
      <div className="flex items-center gap-2.5">
        <h1 className="text-[28px] font-extrabold tracking-tight text-slate-900">AI 사건 경위서 작성</h1>
        <span className="rounded-[5px] bg-indigo-50 px-[7px] py-[3px] text-[10.5px] font-extrabold text-indigo-600">
          NEW
        </span>
      </div>
      <p className="mt-2.5 text-[14.5px] leading-relaxed text-slate-600">
        피해 상황을 아는 대로 적어주세요. 경찰 제출용 진술서 문체로 정리해 드립니다.
      </p>

      <div className="mt-[22px] rounded-[18px] border border-slate-200 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
        <div className="text-[13px] font-bold text-slate-900">1 · 피해 상황 설명</div>
        <Textarea
          value={situation}
          onChange={(e) => setSituation(e.target.value)}
          placeholder="언제, 어떤 경로로 연락을 받았고, 무엇을 전달했는지 시간 순서대로 적어주세요. 금액·계좌·상대방 아이디를 기억나는 대로 포함하면 더 정확합니다."
          className="mt-2.5 min-h-[150px] resize-y border-slate-200 bg-slate-50 focus-visible:ring-indigo-500"
        />

        <div className="mt-[18px] flex items-center gap-2 text-[13px] font-bold text-slate-900">
          2 · 증거 캡처 <span className="font-medium text-slate-400">선택</span>
        </div>

        {previewUrl ? (
          <div className="relative mt-2.5 overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={previewUrl} alt="업로드한 증거 캡처 미리보기" className="max-h-56 w-full object-contain" />
            <button
              type="button"
              onClick={clearFile}
              aria-label="이미지 제거"
              className="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-full bg-black/60 text-white transition hover:bg-black/80"
            >
              <X className="h-4 w-4" aria-hidden />
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              handleFile(e.dataTransfer.files[0]);
            }}
            className={`mt-2.5 flex w-full flex-col items-center gap-2 rounded-xl border-2 border-dashed p-[26px] text-center transition-colors ${
              dragOver ? "border-indigo-400 bg-indigo-50" : "border-slate-300 bg-slate-50 hover:bg-slate-100"
            }`}
          >
            <UploadCloud className={`h-6 w-6 ${dragOver ? "text-indigo-500" : "text-slate-400"}`} aria-hidden />
            <p className="text-[13.5px] font-medium text-slate-700">대화 캡처·송금 내역을 끌어다 놓으세요</p>
            <p className="font-mono text-xs text-slate-500">PNG · JPG · 최대 10MB</p>
          </button>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />

        <div className="mt-[18px] flex items-center gap-3.5">
          <button
            type="button"
            disabled={generating}
            onClick={handleGenerateClick}
            className="rounded-[11px] bg-indigo-600 px-[22px] py-3 text-sm font-bold text-white transition hover:bg-indigo-700 disabled:opacity-60"
          >
            경위서 생성하기
          </button>
          {generating && (
            <span className="flex items-center gap-2 text-[13px] text-slate-600">
              <Spinner className="h-4 w-4" /> 진술서 문체로 정리 중…
            </span>
          )}
        </div>

        {error && (
          <div className="mt-3.5 flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            <AlertCircle className="h-4 w-4 shrink-0" aria-hidden />
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="mt-3.5 overflow-hidden rounded-[18px] border border-slate-200 bg-white shadow-[0_1px_3px_rgba(15,23,42,0.06)]">
          <div className="flex flex-wrap items-center gap-3 border-b border-slate-100 px-[22px] py-[18px]">
            <div className="text-[15px] font-bold text-slate-900">생성된 경위서</div>
            <div className="text-xs text-slate-400">제출 전 사실관계를 반드시 확인하세요</div>
            <button
              type="button"
              onClick={copyAll}
              className="ml-auto rounded-[10px] bg-slate-900 px-4 py-2.5 text-[13px] font-bold text-white transition hover:bg-slate-700"
            >
              {copied ? "복사 완료" : "전체 복사"}
            </button>
          </div>
          <div className="px-[22px] pb-[22px] pt-1.5">
            {toSections(result).map((sec) => (
              <div key={sec.key} className="border-b border-slate-50 py-[18px] last:border-0">
                <div className="text-[11.5px] font-bold tracking-wider text-indigo-600">{sec.key}</div>
                <div className="mt-1.5 text-[14.5px] font-bold text-slate-900">{sec.title}</div>
                <div className="mt-2 whitespace-pre-line text-[13.5px] leading-[1.85] text-slate-700">
                  {sec.body}
                </div>
              </div>
            ))}
            <div className="mt-[18px] flex flex-wrap gap-2.5">
              <a
                href="/scan/guide"
                className="rounded-[10px] border border-slate-200 px-[18px] py-[11px] text-[13.5px] font-semibold text-slate-900 transition hover:bg-slate-50"
              >
                대응 가이드로 돌아가기
              </a>
              <a
                href="tel:112"
                className="rounded-[10px] border border-slate-200 px-[18px] py-[11px] text-[13.5px] font-semibold text-slate-900 transition hover:bg-slate-50"
              >
                경찰 112 연결
              </a>
            </div>
          </div>
        </div>
      )}

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent showCloseButton={false} className="max-w-[430px] gap-0 rounded-2xl p-[22px]">
          <div className="flex items-center gap-2">
            <span className="h-[9px] w-[9px] rounded-sm bg-amber-500" aria-hidden />
            <DialogTitle className="text-[16.5px] font-extrabold tracking-tight text-slate-900">
              제출 전 반드시 확인하세요
            </DialogTitle>
          </div>
          <DialogDescription className="mt-2.5 text-[13.5px] leading-relaxed text-slate-600">
            AI가 작성하는 것은 <b className="text-slate-900">초안</b>입니다. 사실과 다른 내용이 포함되면
            수사에 혼선이 생기고 진술의 신뢰도가 떨어질 수 있으므로, 생성 후 날짜·금액·인물을 직접
            확인하고 수정해 제출하세요.
          </DialogDescription>
          <div className="mt-[18px] flex gap-[9px]">
            <button
              type="button"
              onClick={confirmGenerate}
              className="flex-1 rounded-[11px] bg-indigo-600 py-3 text-[13.5px] font-bold text-white transition hover:bg-indigo-700"
            >
              확인했습니다, 생성하기
            </button>
            <button
              type="button"
              onClick={() => setConfirmOpen(false)}
              className="rounded-[11px] border border-slate-200 px-4 py-3 text-[13.5px] font-semibold text-slate-600 hover:bg-slate-50"
            >
              취소
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
