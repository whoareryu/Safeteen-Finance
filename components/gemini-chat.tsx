"use client";

import {
  ChevronDown,
  Mic,
  Plus,
  SendHorizontal,
  SlidersHorizontal,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

type Role = "user" | "assistant";

type Msg = { id: string; role: Role; content: string };

const MODEL_OPTIONS = [
  { value: "gemini-2.5-flash", label: "빠른 모델" },
  { value: "gemini-2.0-flash", label: "Gemini 2.0 Flash" },
] as const;

function id() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export default function GeminiChat() {
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
      };

      if (!res.ok) {
        const msg =
          typeof data.message === "string"
            ? data.message
            : typeof data.error === "string"
              ? data.error
              : "요청에 실패했습니다.";
        setError(msg);
        return;
      }
      if (!data.text) {
        setError("응답이 비어 있습니다.");
        return;
      }
      setMessages((prev) => [...prev, { id: id(), role: "assistant", content: data.text! }]);
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

  return (
    <div className="mx-auto w-full max-w-xl">
      {hasThread && (
        <div
          ref={listRef}
          className="mb-3 max-h-[min(40vh,220px)] space-y-2 overflow-y-auto rounded-2xl border border-border/40 bg-card/30 px-3 py-2 text-left text-sm"
        >
          {messages.map((m) => (
            <div
              key={m.id}
              className={
                m.role === "user"
                  ? "ml-6 rounded-xl rounded-br-sm bg-primary/15 px-2.5 py-1.5 text-foreground"
                  : "mr-4 rounded-xl rounded-bl-sm bg-muted/40 px-2.5 py-1.5 text-foreground/90"
              }
            >
              <p className="whitespace-pre-wrap break-words">{m.content}</p>
            </div>
          ))}
          {loading && (
            <div className="mr-4 rounded-xl rounded-bl-sm bg-muted/40 px-2.5 py-1.5 text-muted-foreground">
              답변 작성 중…
            </div>
          )}
        </div>
      )}

      {/* 입력 영역은 세로 중앙에 두고, 전체 폭은 Gemini 웹에 가깝게 좁게 */}
      <div className="flex min-h-[136px] w-full min-w-0 flex-col rounded-[28px] border border-white/[0.12] bg-[#1e1f20] px-4 pb-2.5 pt-3 text-[#e3e3e3] shadow-xl md:min-h-[152px]">
        <div className="flex min-h-[84px] flex-1 flex-col justify-center py-1">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Gemini에게 물어보기"
            disabled={loading}
            className="w-full max-h-[120px] min-h-[26px] resize-none overflow-y-auto bg-transparent text-left text-[15px] leading-relaxed text-[#f1f3f4] placeholder:text-[#9aa0a6] outline-none disabled:opacity-60"
          />
        </div>

        {error && (
          <p className="mb-1 shrink-0 text-xs text-red-400" role="alert">
            {error}
          </p>
        )}

        <div className="mt-0.5 flex shrink-0 items-center justify-between gap-2 border-t border-white/[0.08] pt-2.5">
          <div className="flex items-center gap-0.5">
            <button
              type="button"
              className="rounded-full p-2 text-[#c4c7c5] transition-colors hover:bg-white/10 hover:text-[#e8eaed]"
              aria-label="첨부 (준비 중)"
              title="준비 중"
            >
              <Plus className="size-5" strokeWidth={1.75} />
            </button>
            <button
              type="button"
              className="flex items-center gap-1.5 rounded-full px-2 py-1.5 text-sm text-[#c4c7c5] transition-colors hover:bg-white/10 hover:text-[#e8eaed]"
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
                  setModel(e.target.value as (typeof MODEL_OPTIONS)[number]["value"])
                }
                className="appearance-none rounded-full border border-white/15 bg-white/[0.06] py-1.5 pl-3 pr-8 text-sm text-[#e8eaed] outline-none hover:bg-white/10 disabled:opacity-50"
                aria-label="모델 선택"
              >
                {MODEL_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value} className="bg-[#1e1f20]">
                    {o.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-2 top-1/2 size-4 -translate-y-1/2 text-[#9aa0a6]" />
            </div>

            <button
              type="button"
              className="rounded-full p-2 text-[#c4c7c5] opacity-60"
              aria-label="음성 입력 (미지원)"
              title="미지원"
              disabled
            >
              <Mic className="size-5" strokeWidth={1.75} />
            </button>
          </div>
        </div>
      </div>

      <p className="mx-auto mt-2.5 max-w-xl px-2 text-center text-[11px] leading-snug text-[#8e918f] sm:text-xs">
        Gemini는 AI이며 인물 등에 관한 정보 제공 시 실수를 할 수 있습니다.{" "}
        <a
          href="https://gemini.google.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[#a8c7fa] underline decoration-[#a8c7fa]/70 underline-offset-2 hover:text-[#c5d8fc]"
        >
          개인 정보 보호 및 Gemini
        </a>
      </p>
    </div>
  );
}
