"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, ShieldAlert, Sparkles, UploadCloud, X } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { analyzeContent } from "@/lib/safeteen-api";
import { useScanResult } from "@/components/scan-result-context";

const SAMPLES = [
  {
    label: "무직자 당일 대출 광고",
    text: "신불자·무직자 가능. 서류 없이 당일 300까지. 심사 없이 바로 입금됩니다. 상담은 텔레그램으로만.",
  },
  {
    label: "휴대폰 개통 알바 DM",
    text: "휴대폰 개통만 도와주시면 현금 200 드립니다. 명의만 빌려주시면 되고 요금은 저희가 냅니다.",
  },
  {
    label: "통장 대여 구인글",
    text: "단순 입출금 업무. 본인 명의 통장과 체크카드만 있으면 일당 30만원. 초보 가능.",
  },
];

export default function ScannerSection() {
  const router = useRouter();
  const { setResult } = useScanResult();
  const [tab, setTab] = useState<"text" | "image">("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [invalid, setInvalid] = useState(false);
  const [showMask, setShowMask] = useState(false);
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

  async function runAnalyze() {
    setShowMask(false);
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

  function handleSubmit() {
    if (loading) return;
    if (!canSubmit) {
      setInvalid(true);
      return;
    }
    setInvalid(false);
    // 이미지가 있으면 분석 전에 개인정보 마스킹 확인을 한 번 거친다.
    if (file) {
      setShowMask(true);
      return;
    }
    runAnalyze();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900 sm:text-2xl">AI 스캐너</h1>
        <p className="mt-1 text-sm text-slate-500">
          의심되는 대출·구인 광고를 붙여넣거나 캡처 이미지를 올려주세요. 개인정보는 자동으로 가려진 뒤
          분석됩니다.
        </p>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="sr-only">
          <CardTitle>광고 내용 입력</CardTitle>
          <CardDescription>텍스트를 붙여넣거나, SNS 캡처 이미지를 업로드하세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={tab} onValueChange={(v) => setTab(v as "text" | "image")} className="w-full">
            <TabsList>
              <TabsTrigger value="text">텍스트 붙여넣기</TabsTrigger>
              <TabsTrigger value="image">이미지 업로드</TabsTrigger>
            </TabsList>

            <TabsContent value="text" className="mt-4 space-y-3">
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="예: 신불자 가능, 무직자 당일 대출. 휴대폰 개통만 도와주시면 현금 200 드립니다."
                className="min-h-40 resize-y border-slate-200 bg-slate-50 focus-visible:ring-indigo-500"
              />
              <div>
                <div className="text-xs font-semibold text-slate-500">예시로 바로 체험해보기</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {SAMPLES.map((s) => (
                    <Button
                      key={s.label}
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setText(s.text)}
                      className="border-slate-200 bg-slate-50 text-slate-700 hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-800"
                    >
                      <Sparkles className="h-3.5 w-3.5" aria-hidden />
                      {s.label}
                    </Button>
                  ))}
                </div>
              </div>
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
                  <p className="text-sm font-medium text-slate-700">캡처 이미지를 여기에 끌어다 놓으세요</p>
                  <p className="text-xs text-slate-400">PNG · JPG · 최대 10MB</p>
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

          <div className="mt-[18px] flex flex-wrap items-center gap-3 border-t border-slate-100 pt-[18px]">
            <Button
              type="button"
              disabled={loading}
              onClick={handleSubmit}
              className="h-auto rounded-[11px] bg-indigo-600 px-[22px] py-3 text-sm font-bold text-white shadow-sm hover:bg-indigo-700"
            >
              {loading ? <Spinner className="h-4 w-4" /> : <ShieldAlert className="h-4 w-4" aria-hidden />}
              위험도 진단하기
            </Button>
            {loading ? (
              <div className="flex items-center gap-2 text-[13px] text-slate-600">
                <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-600" aria-hidden />
                은어 사전 대조 · 법률 매칭 · 팩트체크 중…
              </div>
            ) : invalid ? (
              <div className="flex items-center gap-2 rounded-[9px] border border-rose-200 bg-rose-50 px-3 py-2 text-[12.5px] font-semibold text-rose-700">
                <span className="h-1.5 w-1.5 rounded-full bg-rose-600" aria-hidden />
                진단할 문구를 붙여넣거나 아래 예시를 선택해 주세요.
              </div>
            ) : (
              <div className="text-[12.5px] text-slate-400">평균 3초 소요 · 입력 내용은 저장되지 않습니다</div>
            )}
          </div>
        </CardContent>
      </Card>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <AlertCircle className="h-4 w-4 shrink-0" aria-hidden />
          {error}
        </div>
      ) : null}

      <Dialog open={showMask} onOpenChange={setShowMask}>
        <DialogContent showCloseButton={false} className="max-w-[460px] gap-0 rounded-2xl p-[22px]">
          <DialogTitle className="text-[17px] font-extrabold tracking-tight text-slate-900">
            이 이미지를 그대로 분석할까요?
          </DialogTitle>
          <DialogDescription className="mt-2 text-[13px] leading-relaxed text-slate-600">
            업로드한 캡처가 AI 분석 서버로 전송됩니다. 상대방 계좌번호·연락처처럼 신고에 필요한 정보는
            남겨도 괜찮지만, 본인의 주민등록번호·카드번호처럼 민감한 정보가 함께 찍혀 있다면 가리고
            올려주세요.
          </DialogDescription>
          <div className="mt-3.5 overflow-hidden rounded-[14px] border border-slate-200">
            {previewUrl && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={previewUrl} alt="업로드한 캡처 미리보기" className="max-h-40 w-full object-contain bg-slate-50" />
            )}
          </div>
          <div className="mt-[18px] flex gap-[9px]">
            <Button
              type="button"
              onClick={runAnalyze}
              className="h-auto flex-1 rounded-[11px] bg-indigo-600 py-3 text-[13.5px] font-bold text-white hover:bg-indigo-700"
            >
              이대로 분석하기
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowMask(false)}
              className="h-auto rounded-[11px] border-slate-200 py-3 text-[13.5px] font-semibold text-slate-600 hover:bg-slate-50"
            >
              취소
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
