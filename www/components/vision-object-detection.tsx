"use client";

import { useCallback, useRef, useState } from "react";
import { ImageIcon, Loader2, ScanFace, Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

type YoloPredictResponse = {
  name: string;
  confidence: number;
};

type PredictResult = {
  ok: boolean;
  name?: string;
  confidence?: number;
  message?: string;
};

const YOLO_PREDICT_ENDPOINT = "/api/vision/yolo-predict";

export default function VisionObjectDetection() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResult | null>(null);

  const pickFile = useCallback((f: File | null) => {
    if (!f) return;
    if (!f.type.startsWith("image/")) {
      setResult({ ok: false, message: "이미지 파일만 선택할 수 있습니다." });
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
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

  const predict = async () => {
    if (!file || loading) return;
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(YOLO_PREDICT_ENDPOINT, {
        method: "POST",
        body: formData,
      });
      const payload = (await res.json().catch(() => null)) as
        | YoloPredictResponse
        | { detail?: string }
        | null;
      if (!res.ok) {
        const detail =
          payload && typeof payload === "object" && "detail" in payload
            ? payload.detail
            : undefined;
        throw new Error(typeof detail === "string" ? detail : "예측에 실패했습니다.");
      }
      const data = payload as YoloPredictResponse;
      setResult({ ok: true, name: data.name, confidence: data.confidence });
    } catch (e) {
      const message = e instanceof Error ? e.message : "예측 중 오류가 발생했습니다.";
      setResult({ ok: false, message });
    } finally {
      setLoading(false);
    }
  };

  const confidencePercent =
    result?.ok && typeof result.confidence === "number"
      ? (result.confidence * 100).toFixed(1)
      : null;

  return (
    <div className="vision-object-detection w-full max-w-none">
      <h2 className="text-xl font-semibold text-foreground">2. 객체 탐지</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        사람 얼굴 사진을 업로드하면 학습된 YOLO 모델이 인물 이름과 확신도(%)를 예측합니다.
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
            : "border-border bg-card hover:border-primary/40 hover:bg-muted/50"
        )}
      >
        {preview ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={preview}
            alt="선택한 얼굴 이미지 미리보기"
            className="max-h-40 rounded-lg object-contain"
          />
        ) : (
          <>
            <Upload className="h-10 w-10 text-muted-foreground" aria-hidden />
            <p className="mt-3 text-center text-sm font-medium text-foreground">
              얼굴 이미지를 여기에 끌어다 놓거나 클릭해 선택
            </p>
            <p className="mt-1 text-center text-xs text-muted-foreground">JPG, PNG 등</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="sr-only"
          onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {file ? (
        <div className="mt-4 flex flex-wrap items-center gap-3 rounded-xl border border-border bg-card px-4 py-3">
          <ImageIcon className="h-5 w-5 shrink-0 text-[#0071e3]" aria-hidden />
          <span className="min-w-0 flex-1 truncate text-sm text-foreground">
            {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </span>
          <Button
            type="button"
            variant="ghost"
            onClick={() => void predict()}
            disabled={loading}
            className="apple-cta-primary rounded-full px-5 hover:bg-[#0071e3]"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                예측 중…
              </>
            ) : (
              "인물 예측"
            )}
          </Button>
        </div>
      ) : null}

      {result?.ok ? (
        <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3">
          <div className="flex items-center gap-2">
            <ScanFace className="h-5 w-5 text-emerald-700" aria-hidden />
            <span className="text-sm font-semibold text-emerald-900">
              예측 결과: {result.name}
            </span>
          </div>
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs text-emerald-800">
              <span>일치율</span>
              <span className="font-semibold">{confidencePercent}%</span>
            </div>
            <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-emerald-100">
              <div
                className="h-full rounded-full bg-emerald-600"
                style={{ width: `${confidencePercent}%` }}
              />
            </div>
          </div>
        </div>
      ) : result && !result.ok ? (
        <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700" role="status">
          {result.message}
        </p>
      ) : null}
    </div>
  );
}
