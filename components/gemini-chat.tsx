"use client";

import {
  ChevronDown,
  Mic,
  Plus,
  SendHorizontal,
  SlidersHorizontal,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

type Role = "user" | "assistant";

type Msg = { id: string; role: Role; content: string };

const MODEL_OPTIONS = [
  { value: "gemini-2.5-flash", label: "빠른 모델" },
  { value: "gemini-2.0-flash", label: "Gemini 2.0 Flash" },
] as const;

function id() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

type GeminiChatProps = {
  variant?: "dark" | "apple";
};

export default function GeminiChat({ variant = "dark" }: GeminiChatProps) {
  const isApple = variant === "apple";
  const neonShield = isApple ? "neon-hit-shield" : "";
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState<(typeof MODEL_OPTIONS)[number]["value"]>(
    "gemini-2.5-flash"
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollBottom = useCallback(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, []);

  useEffect(() => {
    scrollBottom();
  }, [messages, loading, scrollBottom]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    setError(null);
    setInput("");
    const userMsg: Msg = { id: id(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    const history: { role: Role; content: string }[] = [
      ...messages.map((m) => ({ role: m.role, content: m.content })),
      { role: "user", content: text },
    ];

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history, model }),
      });
      const data = (await res.json()) as {
        text?: string;
        model?: string;
        error?: boolean | string;
        message?: string;
        detail?: string | unknown;
      };

      if (!res.ok) {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : Array.isArray(data.detail)
              ? "요청 형식이 올바르지 않습니다."
              : null;
        const msg =
          detail ??
          (typeof data.message === "string"
            ? data.message
            : typeof data.error === "string"
              ? data.error
              : res.status === 502
                ? "백엔드 또는 Gemini API 연결에 실패했습니다. backend 서버와 GEMINI_API_KEY를 확인하세요."
                : "요청에 실패했습니다.");
        setError(msg);
        return;
      }
      if (!data.text) {
        setError("응답이 비어 있습니다.");
        return;
      }
      setMessages((prev) => [
        ...prev,
        { id: id(), role: "assistant", content: data.text! },
      ]);
    } catch {
      setError("네트워크 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }, [input, loading, messages, model]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "0px";
    ta.style.height = `${Math.min(Math.max(ta.scrollHeight, 26), 120)}px`;
  }, [input]);

  const hasThread = messages.length > 0 || loading;
  const canSend = input.trim().length > 0 && !loading;

  const iconBtn = isApple
    ? "rounded-full p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
    : "rounded-full p-2 text-[#c4c7c5] transition-colors hover:bg-white/10 hover:text-[#e8eaed]";

  const toolBtn = isApple
    ? "flex items-center gap-1.5 rounded-full border border-border bg-card px-2.5 py-1.5 text-sm text-foreground shadow-sm transition-colors hover:bg-secondary"
    : "flex items-center gap-1.5 rounded-full px-2 py-1.5 text-sm text-[#c4c7c5] transition-colors hover:bg-white/10 hover:text-[#e8eaed]";

  return (
    <div className="mx-auto w-full max-w-xl">
      <div
        className={cn(
          "gemini-chat-shell flex min-h-[136px] w-full min-w-0 flex-col rounded-[28px] px-4 pb-2.5 pt-3 md:min-h-[152px]",
          neonShield,
          isApple
            ? "border border-border bg-card text-foreground shadow-sm"
            : "border border-white/[0.12] bg-[#1e1f20] text-[#e3e3e3] shadow-xl"
        )}
      >
        <div className="flex min-h-[84px] flex-1 flex-col justify-center py-1">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Gemini에게 물어보기"
            disabled={loading}
            className={cn(
              "w-full max-h-[120px] min-h-[26px] resize-none overflow-y-auto bg-transparent text-left text-[15px] leading-relaxed outline-none disabled:opacity-60",
              isApple
                ? "text-foreground placeholder:text-muted-foreground"
                : "text-[#f1f3f4] placeholder:text-[#9aa0a6]"
            )}
          />
        </div>

        {error && (
          <p
            className={cn(
              "mb-1 shrink-0 text-xs",
              isApple ? "text-red-600" : "text-red-400"
            )}
            role="alert"
          >
            {error}
          </p>
        )}

        <div
          className={cn(
            "mt-0.5 flex shrink-0 items-center justify-between gap-2 border-t pt-2.5",
            isApple ? "border-border" : "border-white/[0.08]"
          )}
        >
          <div className="flex items-center gap-0.5">
            <button
              type="button"
              className={iconBtn}
              aria-label="첨부 (준비 중)"
              title="준비 중"
            >
              <Plus className="size-5" strokeWidth={1.75} />
            </button>
            <button
              type="button"
              className={toolBtn}
              aria-label="도구 (준비 중)"
              title="준비 중"
            >
              <SlidersHorizontal className="size-4" strokeWidth={1.75} />
              <span>도구</span>
            </button>
          </div>

          <div className="flex items-center gap-0.5">
            <div className="relative">
              <select
                value={model}
                disabled={loading}
                onChange={(e) =>
                  setModel(
                    e.target.value as (typeof MODEL_OPTIONS)[number]["value"]
                  )
                }
                className={cn(
                  "appearance-none rounded-full border py-1.5 pl-3 pr-8 text-sm outline-none disabled:opacity-50",
                  isApple
                    ? "border-border bg-card text-foreground hover:bg-secondary"
                    : "border-white/15 bg-white/[0.06] text-[#e8eaed] hover:bg-white/10"
                )}
                aria-label="모델 선택"
              >
                {MODEL_OPTIONS.map((o) => (
                  <option
                    key={o.value}
                    value={o.value}
                    className={isApple ? "bg-card text-foreground" : "bg-[#1e1f20]"}
                  >
                    {o.label}
                  </option>
                ))}
              </select>
              <ChevronDown
                className={cn(
                  "pointer-events-none absolute right-2 top-1/2 size-4 -translate-y-1/2",
                  isApple ? "text-muted-foreground" : "text-[#9aa0a6]"
                )}
              />
            </div>

            <button
              type="button"
              className={cn(iconBtn, !isApple && "opacity-60")}
              aria-label="음성 입력 (미지원)"
              title="미지원"
              disabled
            >
              <Mic className="size-5" strokeWidth={1.75} />
            </button>

            <button
              type="button"
              onClick={() => void send()}
              disabled={!canSend}
              className={cn(
                "rounded-full p-2 transition-colors disabled:cursor-not-allowed",
                isApple
                  ? canSend
                    ? "bg-primary text-primary-foreground hover:opacity-90"
                    : "text-muted-foreground/50"
                  : canSend
                    ? "bg-[#8ab4f8] text-[#1e1f20] hover:bg-[#a8c7fa]"
                    : "text-[#5f6368] opacity-60"
              )}
              aria-label="전송"
              title="전송"
            >
              <SendHorizontal className="size-5" strokeWidth={1.75} />
            </button>
          </div>
        </div>
      </div>

      {hasThread && (
        <div
          ref={listRef}
          className={cn(
            "mt-3 max-h-[min(40vh,220px)] space-y-2 overflow-y-auto rounded-2xl border px-3 py-2 text-left text-sm",
            neonShield,
            isApple
              ? "border-border bg-card shadow-sm"
              : "border-border/40 bg-card/30"
          )}
        >
          {messages.map((m) => (
            <div
              key={m.id}
              className={cn(
                "rounded-xl px-2.5 py-1.5",
                m.role === "user"
                  ? isApple
                    ? "ml-6 rounded-br-sm border border-border bg-card text-foreground"
                    : "ml-6 rounded-br-sm bg-primary/15 text-foreground"
                  : isApple
                    ? "mr-4 rounded-bl-sm bg-secondary text-foreground"
                    : "mr-4 rounded-bl-sm bg-muted/40 text-foreground/90"
              )}
            >
              <p className="whitespace-pre-wrap break-words">{m.content}</p>
            </div>
          ))}
          {loading && (
            <div
              className={cn(
                "mr-4 rounded-xl rounded-bl-sm px-2.5 py-1.5",
                isApple
                  ? "bg-secondary text-muted-foreground"
                  : "bg-muted/40 text-muted-foreground"
              )}
            >
              답변 작성 중…
            </div>
          )}
        </div>
      )}

      <p
        className={cn(
          "mx-auto mt-2.5 max-w-xl px-2 text-center text-[11px] leading-snug sm:text-xs",
          isApple && "neon-text-shield",
          isApple ? "text-muted-foreground" : "text-[#8e918f]"
        )}
      >
        Gemini는 AI이며 인물 등에 관한 정보 제공 시 실수를 할 수 있습니다.{" "}
        <a
          href="https://gemini.google.com"
          target="_blank"
          rel="noopener noreferrer"
          className={cn(
            "underline underline-offset-2",
            isApple
              ? "text-blue-600 decoration-blue-600/50 hover:text-blue-700"
              : "text-[#a8c7fa] decoration-[#a8c7fa]/70 hover:text-[#c5d8fc]"
          )}
        >
          개인 정보 보호 및 Gemini
        </a>
      </p>
    </div>
  );
}
