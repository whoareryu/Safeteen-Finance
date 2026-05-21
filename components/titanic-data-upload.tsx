"use client";

import { useCallback, useRef, useState } from "react";
import { FileSpreadsheet, Loader2, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

type UploadResult = {
  ok: boolean;
  message?: string;
  inserted?: number;
  deleted_previous?: number;
  table?: string;
  error?: string;
};

export default function TitanicDataUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);

  const pickFile = useCallback((f: File | null) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".csv")) {
      setResult({ ok: false, error: "CSV 파일만 선택할 수 있습니다." });
      return;
    }
    setFile(f);
    setResult(null);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files?.[0];
      pickFile(f ?? null);
    },
    [pickFile]
  );

  const upload = async () => {
    if (!file || loading) return;
    setLoading(true);
    setResult(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/api/titanic/upload", {
        method: "POST",
        body: form,
      });
      const data = (await res.json()) as UploadResult & { detail?: string };
      if (!res.ok) {
        setResult({
          ok: false,
          error:
            data.error ??
            (typeof data.detail === "string" ? data.detail : "업로드에 실패했습니다."),
        });
        return;
      }
      setResult(data);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch {
      setResult({ ok: false, error: "네트워크 오류 — 백엔드 서버를 확인해 주세요." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="titanic-data-upload mx-auto w-full max-w-2xl">
      <h2 className="text-xl font-semibold text-[#1d1d1f]">1. 데이터 수집</h2>
      <p className="mt-2 text-sm leading-relaxed text-[#6e6e73]">
        Kaggle에서 받은 Titanic CSV를 Neon PostgreSQL{" "}
        <code className="rounded bg-black/[0.06] px-1.5 py-0.5 text-xs">
          titanic_passengers
        </code>{" "}
        테이블에 적재합니다. 새 파일을 올리면 기존 데이터는 교체됩니다.
      </p>

      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "mt-6 flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 transition",
          dragOver
            ? "border-[#0071e3] bg-[#0071e3]/5"
            : "border-black/15 bg-white hover:border-black/25 hover:bg-[#f5f5f7]"
        )}
      >
        <Upload className="h-10 w-10 text-[#86868b]" aria-hidden />
        <p className="mt-3 text-center text-sm font-medium text-[#1d1d1f]">
          CSV를 여기에 끌어다 놓거나 클릭해 선택
        </p>
        <p className="mt-1 text-center text-xs text-[#86868b]">
          PassengerId, Survived, Pclass, Name, Sex, Age … (Kaggle 형식)
        </p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          className="sr-only"
          onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {file ? (
        <div className="mt-4 flex flex-wrap items-center gap-3 rounded-xl border border-black/[0.08] bg-white px-4 py-3">
          <FileSpreadsheet className="h-5 w-5 shrink-0 text-[#0071e3]" aria-hidden />
          <span className="min-w-0 flex-1 truncate text-sm text-[#1d1d1f]">
            {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </span>
          <button
            type="button"
            onClick={() => void upload()}
            disabled={loading}
            className="apple-cta-primary inline-flex items-center gap-2 rounded-full px-5 py-2 text-sm disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                Neon에 저장 중…
              </>
            ) : (
              "Neon에 업로드"
            )}
          </button>
        </div>
      ) : null}

      {result ? (
        <p
          className={cn(
            "mt-4 rounded-xl px-4 py-3 text-sm",
            result.ok
              ? "bg-emerald-50 text-emerald-800"
              : "bg-red-50 text-red-700"
          )}
          role="status"
        >
          {result.ok
            ? result.message ??
              `${result.inserted ?? 0}건 저장 완료 (이전 ${result.deleted_previous ?? 0}건 교체)`
            : result.error}
        </p>
      ) : null}
    </div>
  );
}
