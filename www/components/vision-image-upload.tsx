"use client";

import { useCallback, useRef, useState } from "react";
import { ImageIcon, Loader2, Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

type VisionUploadResponse = {
  filename: string;
  content_type: string;
  size: number;
  message: string;
};

type UploadResult = {
  ok: boolean;
  message: string;
};

const VISION_UPLOAD_ENDPOINT = "/api/vision/upload";

export default function VisionImageUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);

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

  const upload = async () => {
    if (!file || loading) return;
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(VISION_UPLOAD_ENDPOINT, {
        method: "POST",
        body: formData,
      });
      const payload = (await res.json().catch(() => null)) as
        | VisionUploadResponse
        | { detail?: string }
        | null;
      if (!res.ok) {
        const detail =
          payload && typeof payload === "object" && "detail" in payload
            ? payload.detail
            : undefined;
        throw new Error(typeof detail === "string" ? detail : "서버 업로드에 실패했습니다.");
      }
      const data = payload as VisionUploadResponse;
      setResult({ ok: true, message: data.message });
    } catch (e) {
      const message = e instanceof Error ? e.message : "이미지 업로드 중 오류가 발생했습니다.";
      setResult({ ok: false, message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vision-image-upload w-full max-w-none">
      <h2 className="text-xl font-semibold text-foreground">1. 이미지 업로드</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        이미지를 업로드하면 백엔드 vision 파이프라인(vision_router.py)으로 전달됩니다.
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
            alt="선택한 이미지 미리보기"
            className="max-h-40 rounded-lg object-contain"
          />
        ) : (
          <>
            <Upload className="h-10 w-10 text-muted-foreground" aria-hidden />
            <p className="mt-3 text-center text-sm font-medium text-foreground">
              이미지를 여기에 끌어다 놓거나 클릭해 선택
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
            onClick={() => void upload()}
            disabled={loading}
            className="apple-cta-primary rounded-full px-5 hover:bg-[#0071e3]"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                업로드 중…
              </>
            ) : (
              "업로드"
            )}
          </Button>
        </div>
      ) : null}

      {result ? (
        <p
          className={cn(
            "mt-4 rounded-xl px-4 py-3 text-sm",
            result.ok ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-700"
          )}
          role="status"
        >
          {result.message}
        </p>
      ) : null}
    </div>
  );
}
