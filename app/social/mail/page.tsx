"use client";

import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { BookUser, Loader2, Send } from "lucide-react";
import { sendEmail, type EmailSendResponse } from "@/lib/chef-email";
import AddressBookPanel from "@/components/address-book-panel";
import EmailAutocomplete from "@/components/email-autocomplete";
import { cn } from "@/lib/utils";
import { useAuth } from "@/components/auth-provider";

const schema = z.object({
  to: z.string().email("올바른 이메일 주소를 입력해주세요"),
  prompt: z.string().min(5, "내용을 5자 이상 입력해주세요"),
});
type FormValues = z.infer<typeof schema>;

export default function MailPage() {
  const { isOwner } = useAuth();
  const [showBook, setShowBook] = useState(false);
  const [result, setResult] = useState<EmailSendResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    control,
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setError(null);
    setResult(null);
    try {
      const res = await sendEmail(values);
      setResult(res);
      reset();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "전송 중 오류가 발생했습니다");
    }
  }

  return (
    <main className="mx-auto flex max-w-4xl gap-4 px-4 pb-28 pt-6">
      {/* ── 왼쪽: 이메일 작성 폼 ── */}
      <div className={cn("flex-1 min-w-0", showBook ? "max-w-[55%]" : "max-w-lg mx-auto w-full")}>
        <div className="mb-5 flex items-center justify-between">
          <h1 className="text-xl font-bold">이메일 작성</h1>
          {isOwner && (
            <button
              type="button"
              onClick={() => setShowBook((v) => !v)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition",
                showBook
                  ? "bg-primary text-white"
                  : "bg-muted text-foreground hover:bg-muted/70"
              )}
            >
              <BookUser className="h-3.5 w-3.5" />
              주소록
            </button>
          )}
        </div>

        {isOwner ? (
          <>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-foreground">받는 사람</label>
                <Controller
                  name="to"
                  control={control}
                  render={({ field }) => (
                    <EmailAutocomplete
                      value={field.value ?? ""}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      error={!!errors.to}
                      placeholder="example@email.com"
                    />
                  )}
                />
                {errors.to && <p className="text-xs text-destructive">{errors.to.message}</p>}
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-foreground">내용</label>
                <textarea
                  rows={5}
                  placeholder={"어떤 이메일을 작성할까요? 간단히 설명해주세요.\n예) 거래처에 미팅 일정 조율 요청 메일"}
                  {...register("prompt")}
                  className={cn(
                    "w-full resize-none rounded-lg border bg-background px-3 py-2.5 text-sm outline-none",
                    "placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/40",
                    errors.prompt ? "border-destructive" : "border-border"
                  )}
                />
                {errors.prompt && <p className="text-xs text-destructive">{errors.prompt.message}</p>}
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className={cn(
                  "flex w-full items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-semibold text-white transition",
                  "bg-primary hover:bg-primary/90 disabled:opacity-50"
                )}
              >
                {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                {isSubmitting ? "AI가 작성 중..." : "전송"}
              </button>
            </form>

            {error && (
              <div className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}

            {result && (
              <div className="mt-6 space-y-3 rounded-xl border bg-muted/40 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  전송된 이메일
                </p>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">받는 사람</p>
                  <p className="text-sm">{result.to}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">제목</p>
                  <p className="text-sm font-medium">{result.subject}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">본문</p>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{result.body}</p>
                </div>
                <p className="text-right text-xs text-primary">✓ 전송 완료</p>
              </div>
            )}
          </>
        ) : (
          <div className="rounded-lg border border-border bg-muted/40 px-4 py-6 text-center text-sm text-muted-foreground">
            본인 계정으로 로그인해야 이용할 수 있습니다.
          </div>
        )}
      </div>

      {/* ── 오른쪽: 주소록 패널 ── */}
      {isOwner && showBook && (
        <div className="w-72 shrink-0">
          <AddressBookPanel
            onSelect={(email) => {
              setValue("to", email, { shouldValidate: true });
            }}
          />
        </div>
      )}
    </main>
  );
}
