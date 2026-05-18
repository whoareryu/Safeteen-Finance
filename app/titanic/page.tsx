"use client";

import { useCallback, useRef, useState } from "react";
import { Upload } from "lucide-react";

async function postCsv(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch("/api/titanic/upload", {
    method: "POST",
    body: formData,
  });
  const data = (await res.json()) as {
    ok?: boolean;
    message?: string;
    error?: string;
    savedAs?: string;
    bytes?: number;
  };
  if (!res.ok || !data.ok) {
    throw new Error(data.error ?? `업로드 실패 (${res.status})`);
  }
  return data;
}

export default function TitanicHomePage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "ok" | "err";
    text?: string;
  }>({ type: "idle" });

  const runUpload = useCallback(async (file: File | undefined | null) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setStatus({ type: "err", text: "CSV 파일만 업로드할 수 있습니다." });
      return;
    }
    setStatus({ type: "loading", text: "업로드 중…" });
    try {
      const data = await postCsv(file);
      setStatus({
        type: "ok",
        text: `${data.message ?? "완료"} (${data.bytes ?? file.size} bytes)`,
      });
    } catch (e) {
      setStatus({
        type: "err",
        text: e instanceof Error ? e.message : "업로드 중 오류",
      });
    }
  }, []);

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    void runUpload(f);
    e.target.value = "";
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const f = e.dataTransfer.files?.[0];
    void runUpload(f);
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const onDragLeave = () => setDragActive(false);

  return (
    <main className="min-h-[calc(100dvh-var(--site-header-height))] bg-background px-4 pb-16 pt-6">
      <div className="mx-auto max-w-lg space-y-10">
        <div className="relative overflow-hidden rounded-2xl border border-neutral-300 shadow-lg">
          <div
            className="absolute inset-0 scale-105 bg-cover bg-center"
            style={{ backgroundImage: "url(/images/titanic-hero.png)" }}
            aria-hidden
          />
          <div className="absolute inset-0 bg-background/55 backdrop-blur-[2px]" aria-hidden />
          <div
            className="absolute inset-0 bg-gradient-to-b from-background/30 via-transparent to-background/85"
            aria-hidden
          />
          <div className="relative z-10 flex flex-col items-center justify-center px-6 py-14 text-center md:py-20">
            <h1 className="font-serif text-5xl font-bold tracking-[0.35em] text-foreground drop-shadow-md md:text-6xl md:tracking-[0.4em]">
              TITANIC
            </h1>
          </div>
        </div>

        <div className="card-light space-y-8 p-6">
          <p className="text-center text-sm text-muted-foreground">
            <code className="rounded-md bg-muted px-1.5 py-0.5 text-foreground">
              titanic.csv
            </code>{" "}
            는 아래 두 가지 방법 중 하나로 업로드할 수 있습니다. 서버에는 항상{" "}
            <code className="rounded-md bg-muted px-1.5 py-0.5 text-foreground">
              uploads/titanic/titanic.csv
            </code>{" "}
            로 저장됩니다.
          </p>

          <div className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              방법 1 — 파일 선택
            </h2>
            <input
              ref={inputRef}
              type="file"
              accept=".csv,text/csv"
              className="hidden"
              onChange={onInputChange}
            />
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              disabled={status.type === "loading"}
              className="btn-white flex w-full items-center justify-center gap-2 px-4 py-3 text-sm font-medium disabled:opacity-50"
            >
              <Upload className="h-4 w-4" />
              CSV 파일 선택…
            </button>
          </div>

          <div className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              방법 2 — 드래그 앤 드롭
            </h2>
            <div
              role="button"
              tabIndex={0}
              onClick={() => inputRef.current?.click()}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
              }}
              className={`flex min-h-[140px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-4 py-8 text-center transition ${
                dragActive
                  ? "border-primary bg-primary/10 text-neutral-800"
                  : "border-border bg-secondary text-muted-foreground hover:border-border hover:bg-muted"
              }`}
            >
              <Upload className="mb-2 h-8 w-8 opacity-70" />
              <span className="text-sm font-medium text-foreground">
                여기로 CSV 파일을 끌어다 놓으세요
              </span>
              <span className="mt-1 text-xs text-muted-foreground">
                (클릭하면 방법 1과 같이 파일 선택창이 열립니다)
              </span>
              <button
                type="button"
                className="mt-3 text-xs text-primary underline underline-offset-2"
                onClick={(e) => {
                  e.stopPropagation();
                  inputRef.current?.click();
                }}
              >
                또는 찾아보기
              </button>
            </div>
          </div>

          {status.type !== "idle" && (
            <p
              className={`rounded-lg px-3 py-2 text-center text-sm ${
                status.type === "ok"
                  ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400"
                  : status.type === "err"
                    ? "bg-destructive/15 text-destructive"
                    : "bg-muted text-muted-foreground"
              }`}
              role="status"
            >
              {status.text}
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
