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

type JamesUploadResponse = {
  ok: boolean;
  message: string;
  count: number;
  columns: string[];
  rows: unknown[];
};

type TitanicRow = {
  PassengerId: number;
  Survived: number;
  Pclass: number;
  Name: string;
  gender: string;
  Age: number | null;
};

const TITANIC_LOCAL_KEY = "titanic_csv_rows_v1";
const JAMES_UPLOAD_ENDPOINT = "/api/titanic/james/upload";

function parseCsv(text: string): TitanicRow[] {
  const lines = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  const header = (lines[0] ?? "").split(",").map((s) => s.trim());
  const idx = (name: string) => header.findIndex((h) => h.toLowerCase() === name.toLowerCase());

  const iPassengerId = idx("PassengerId");
  const iSurvived = idx("Survived");
  const iPclass = idx("Pclass");
  const iName = idx("Name");
  const iGender = idx("Gender");
  const iLegacySex = idx("Sex");
  const iGenderOrLegacySex = iGender >= 0 ? iGender : iLegacySex;
  const iAge = idx("Age");

  if ([iPassengerId, iSurvived, iPclass, iName, iGenderOrLegacySex].some((i) => i < 0)) {
    throw new Error("CSV 헤더가 Titanic 형식이 아닙니다. (PassengerId, Survived, Pclass, Name, Gender 필요)");
  }

  const out: TitanicRow[] = [];
  for (const raw of lines.slice(1)) {
    const line = raw.trim();
    if (!line) continue;
    // 매우 단순 파서: Kaggle Titanic은 Name에 콤마가 포함될 수 있어 최소한의 따옴표 처리
    // (완벽 CSV 파서는 아니지만, 일반 Kaggle 원본은 이 수준으로 충분)
    const cells: string[] = [];
    let cur = "";
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i]!;
      if (ch === "\"") {
        inQuotes = !inQuotes;
        continue;
      }
      if (ch === "," && !inQuotes) {
        cells.push(cur);
        cur = "";
      } else {
        cur += ch;
      }
    }
    cells.push(cur);

    const PassengerId = Number.parseInt((cells[iPassengerId] ?? "").trim(), 10);
    const Survived = Number.parseInt((cells[iSurvived] ?? "").trim(), 10);
    const Pclass = Number.parseInt((cells[iPclass] ?? "").trim(), 10);
    const Name = String((cells[iName] ?? "").trim());
    const gender = String((cells[iGenderOrLegacySex] ?? "").trim());
    const AgeRaw = iAge >= 0 ? (cells[iAge] ?? "").trim() : "";
    const Age = AgeRaw ? Number.parseFloat(AgeRaw) : null;

    if (!Number.isFinite(PassengerId) || !Number.isFinite(Survived) || !Number.isFinite(Pclass)) {
      continue;
    }

    out.push({
      PassengerId,
      Survived,
      Pclass,
      Name,
      gender,
      Age: Age != null && Number.isFinite(Age) ? Age : null,
    });
  }
  return out;
}

type TitanicDataUploadProps = {
  /** 페이지 헤더가 있을 때 중복 제목 숨김 */
  showHeading?: boolean;
};

export default function TitanicDataUpload({ showHeading = true }: TitanicDataUploadProps) {
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
    try {
      const text = await file.text();
      const rows = parseCsv(text);
      if (rows.length === 0) {
        setResult({ ok: false, error: "CSV에서 유효한 행을 찾지 못했습니다." });
        return;
      }

      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(JAMES_UPLOAD_ENDPOINT, {
        method: "POST",
        body: formData,
      });
      const payload = (await res.json().catch(() => null)) as
        | JamesUploadResponse
        | { detail?: string | { message?: string; errors?: string[] } }
        | null;
      if (!res.ok) {
        const detail =
          payload && typeof payload === "object" && "detail" in payload
            ? payload.detail
            : undefined;
        if (typeof detail === "string") {
          throw new Error(detail);
        }
        if (detail && typeof detail === "object") {
          const msg = detail.message ?? "CSV 업로드 검증 실패";
          const first = detail.errors?.[0];
          throw new Error(first ? `${msg}: ${first}` : msg);
        }
        throw new Error("서버 업로드에 실패했습니다.");
      }

      localStorage.setItem(TITANIC_LOCAL_KEY, JSON.stringify(rows));
      setResult({
        ok: true,
        message: `${rows.length}건을 업로드/저장했습니다. 이제 2. 데이터 분석에서 결과를 확인할 수 있어요.`,
        inserted: rows.length,
      });
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (e) {
      const message = e instanceof Error ? e.message : "CSV 처리 중 오류가 발생했습니다. 파일 형식을 확인해 주세요.";
      setResult({ ok: false, error: message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="titanic-data-upload w-full max-w-none">
      {showHeading ? (
        <>
          <h2 className="text-xl font-semibold text-[#1d1d1f]">1. 데이터 수집</h2>
          <p className="mt-2 text-sm leading-relaxed text-[#6e6e73]">
            Kaggle Titanic CSV를 브라우저(로컬)에 저장합니다. 새 파일을 올리면 기존 데이터는
            교체됩니다.
          </p>
        </>
      ) : (
        <p className="text-sm leading-relaxed text-[#6e6e73]">
          Kaggle Titanic CSV를 브라우저(로컬)에 저장합니다. 새 파일을 올리면 기존 데이터는
          교체됩니다.
        </p>
      )}

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
          PassengerId, Survived, Pclass, Name, Gender, Age … (Kaggle 형식)
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
                저장 중…
              </>
            ) : (
              "저장하기"
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
