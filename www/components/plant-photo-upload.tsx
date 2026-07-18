"use client";

import { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ImageIcon, Loader2, Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import { uploadPlantPhoto } from "@/lib/plant-api";
import { useAuth } from "@/components/auth-provider";

const DEFAULT_REGION = "서울";

type UploadResult = {
  ok: boolean;
  message: string;
};

export default function PlantPhotoUpload() {
  const router = useRouter();
  const { user } = useAuth();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const region = user?.region?.trim() || DEFAULT_REGION;
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
      const diagnosis = await uploadPlantPhoto(file, region);
      router.push(`/plant/diagnosis/${diagnosis.id}`);
    } catch (e) {
      const message = e instanceof Error ? e.message : "사진 진단 중 오류가 발생했습니다.";
      setResult({ ok: false, message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="plant-photo-upload w-full max-w-none">
      <h2 className="text-xl font-semibold text-foreground">반려식물 잎사귀 사진 업로드</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        잎사귀 사진을 업로드하면 품종과 증상을 진단하고 케어 처방을 안내해 드려요.
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
          "mt-4 flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 transition",
          dragOver
            ? "border-primary bg-primary/5"
            : "border-border bg-card hover:border-primary/40 hover:bg-muted/50"
        )}
      >
        {preview ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={preview}
            alt="선택한 잎사귀 사진 미리보기"
            className="max-h-40 rounded-lg object-contain"
          />
        ) : (
          <>
            <Upload className="h-10 w-10 text-muted-foreground" aria-hidden />
            <p className="mt-3 text-center text-sm font-medium text-foreground">
              잎사귀 사진을 여기에 끌어다 놓거나 클릭해 선택
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
        <div className="saessak-card mt-4 flex flex-wrap items-center gap-3 px-4 py-3">
          <ImageIcon className="h-5 w-5 shrink-0 text-primary" aria-hidden />
          <span className="min-w-0 flex-1 truncate text-sm text-foreground">
            {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </span>
          <button
            type="button"
            onClick={() => void upload()}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                진단 중…
              </>
            ) : (
              "진단하기"
            )}
          </button>
        </div>
      ) : null}

      {result ? (
        <p
          className={cn(
            "mt-4 rounded-xl px-4 py-3 text-sm",
            result.ok ? "bg-primary/10 text-primary" : "bg-destructive/10 text-destructive"
          )}
          role="status"
        >
          {result.message}
        </p>
      ) : null}
    </div>
  );
}
