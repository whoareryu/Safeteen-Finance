"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, ShieldAlert, Sparkles, UploadCloud, X } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { analyzeContent } from "@/lib/safeteen-api";
import { useScanResult } from "@/components/scan-result-context";

const EXAMPLE_TEXT =
  "고민 없이 즉시 대출 가능! 신용불량자, 무직자 환영합니다. 선입금(수수료) 10만원만 입금하시면 " +
  "당일 500만원까지 내구제 대출 진행해드려요. 명의만 빌려주셔도 매달 수익 지급! 카톡 문의 ↓";

export default function ScannerSection() {
  const router = useRouter();
  const { setResult } = useScanResult();
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const canSubmit = text.trim().length > 0 || file !== null;

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

  async function handleAnalyze() {
    if (!canSubmit || loading) return;
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeContent({ text: text.trim() || undefined, file });
      setResult(result);
      router.push("/scan/report");
    } catch (e) {
      setError(e instanceof Error ? e.message : "분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900 sm:text-2xl">AI 금융 사기 위험도 진단</h1>
        <p className="mt-1 text-sm text-slate-500">
          SNS에서 받은 대출·구인 광고 문구나 캡처 이미지를 올리면 AI가 위험도를 분석해요.
        </p>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">광고 내용 입력</CardTitle>
          <CardDescription>텍스트를 붙여넣거나, SNS 캡처 이미지를 업로드하세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="text" className="w-full">
            <TabsList>
              <TabsTrigger value="text">텍스트 직접 입력</TabsTrigger>
              <TabsTrigger value="image">SNS 캡처 이미지 업로드</TabsTrigger>
            </TabsList>

            <TabsContent value="text" className="mt-4 space-y-3">
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="의심스러운 광고 문구를 붙여넣어 주세요"
                className="min-h-32 resize-none border-slate-200 bg-slate-50 focus-visible:ring-indigo-500"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setText(EXAMPLE_TEXT)}
                className="border-slate-200 text-slate-600 hover:bg-slate-100"
              >
                <Sparkles className="h-3.5 w-3.5" aria-hidden />
                인스타 내구제 대출 광고 예시 불러오기
              </Button>
            </TabsContent>

            <TabsContent value="image" className="mt-4">
              {previewUrl ? (
                <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={previewUrl} alt="업로드한 캡처 미리보기" className="max-h-64 w-full object-contain" />
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
                  className={`flex w-full flex-col items-center gap-2 rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
                    dragOver ? "border-indigo-400 bg-indigo-50" : "border-slate-200 bg-slate-50 hover:bg-slate-100"
                  }`}
                >
                  <UploadCloud className={`h-8 w-8 ${dragOver ? "text-indigo-500" : "text-slate-400"}`} aria-hidden />
                  <p className="text-sm font-medium text-slate-700">이미지를 드래그하거나 클릭해서 업로드하세요</p>
                  <p className="text-xs text-slate-400">PNG, JPG (최대 10MB)</p>
                </button>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleFile(e.target.files?.[0])}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <AlertCircle className="h-4 w-4 shrink-0" aria-hidden />
          {error}
        </div>
      ) : null}

      <Button
        type="button"
        size="lg"
        disabled={!canSubmit || loading}
        onClick={handleAnalyze}
        className="h-12 w-full bg-indigo-600 text-base font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading ? (
          <>
            <Spinner className="h-4 w-4" />
            AI가 분석하고 있어요...
          </>
        ) : (
          <>
            <ShieldAlert className="h-5 w-5" aria-hidden />
            AI 금융 사기 위험도 진단하기
          </>
        )}
      </Button>
    </div>
  );
}
