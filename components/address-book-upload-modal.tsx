"use client";

import { useCallback, useRef, useState } from "react";
import { FileSpreadsheet, Loader2, Upload, X } from "lucide-react";
import { uploadContactsFile } from "@/lib/chef-address";
import { useAuth } from "@/components/auth-provider";
import { cn } from "@/lib/utils";

type Props = {
  onClose: () => void;
  onSaved: () => void;
};

export default function AddressBookUploadModal({ onClose, onSaved }: Props) {
  const { user } = useAuth();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ ok: boolean; message: string } | null>(null);

  const pickFile = useCallback((f: File | null) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".csv")) {
      setResult({ ok: false, message: "CSV 파일만 선택할 수 있습니다." });
      return;
    }
    setFile(f);
    setResult(null);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      pickFile(e.dataTransfer.files?.[0] ?? null);
    },
    [pickFile]
  );

  const upload = async () => {
    if (!file || loading || !user) return;
    setLoading(true);
    setResult(null);
    try {
      const { saved } = await uploadContactsFile(file);
      setResult({ ok: true, message: `${saved}명을 등록했습니다.` });
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
      onSaved();
    } catch (e) {
      setResult({ ok: false, message: e instanceof Error ? e.message : "파일 처리 중 오류가 발생했습니다." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        {/* 헤더 */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-[#1d1d1f]">주소록 CSV 업로드</h2>
          <button type="button" onClick={onClose} className="rounded-full p-1 hover:bg-muted">
            <X className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>

        <p className="mb-4 text-sm text-[#6e6e73]">
          아래 두 형식을 모두 지원합니다.
          <br />
          <span className="font-medium text-[#1d1d1f]">Google 연락처</span> 내보내기 파일 그대로 사용 가능
          <br />
          <span className="font-medium text-[#1d1d1f]">커스텀 CSV</span>:{" "}
          <code className="rounded bg-muted px-1">name</code>,{" "}
          <code className="rounded bg-muted px-1">email</code> 컬럼 필요
        </p>

        {/* 드롭존 */}
        <div
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") inputRef.current?.click(); }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          className={cn(
            "flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-8 transition",
            dragOver
              ? "border-primary bg-primary/5"
              : "border-black/15 bg-[#f5f5f7] hover:border-black/25 hover:bg-white"
          )}
        >
          <Upload className="h-9 w-9 text-[#86868b]" aria-hidden />
          <p className="mt-3 text-center text-sm font-medium text-[#1d1d1f]">
            CSV를 여기에 끌어다 놓거나 클릭해 선택
          </p>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,text/csv"
            className="sr-only"
            onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
          />
        </div>

        {/* 선택된 파일 */}
        {file && (
          <div className="mt-4 flex items-center gap-3 rounded-xl border border-black/[0.08] bg-white px-4 py-3">
            <FileSpreadsheet className="h-5 w-5 shrink-0 text-primary" aria-hidden />
            <span className="min-w-0 flex-1 truncate text-sm text-[#1d1d1f]">
              {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </span>
            <button
              type="button"
              onClick={() => void upload()}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-1.5 text-sm font-medium text-white disabled:opacity-50"
            >
              {loading ? <><Loader2 className="h-3.5 w-3.5 animate-spin" />저장 중…</> : "저장하기"}
            </button>
          </div>
        )}

        {/* 결과 */}
        {result && (
          <p className={cn("mt-3 rounded-xl px-4 py-3 text-sm", result.ok ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-700")}>
            {result.message}
          </p>
        )}
      </div>
    </div>
  );
}
