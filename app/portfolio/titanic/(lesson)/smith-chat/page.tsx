"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { SendHorizontal, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type Msg = { role: "user" | "assistant"; content: string };

const INITIAL: Msg = {
  role: "assistant",
  content:
    "안녕하십니까. 저는 RMS 타이타닉의 선장 에드워드 존 스미스입니다.\n타이타닉에 관해 궁금한 것이 있으시면 무엇이든 물어보십시오.",
};

export default function SmithChatPage() {
  const [messages, setMessages] = useState<Msg[]>([INITIAL]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: text }]);

    try {
      const history = messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role, text: m.content }));
      const payload = { messages: [...history, { role: "user" as const, text }] };
      const res = await fetch("/api/titanic/smith/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = (await res.json().catch(() => ({}))) as { reply?: string; error?: string };
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply ?? data.error ?? "응답을 받지 못했습니다.",
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "서버에 연결할 수 없습니다." },
      ]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  }, [input, loading]);

  return (
    <div className="flex h-[calc(100dvh-var(--site-header-height)-4rem)] flex-col gap-4">
      <header className="pt-1">
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-[#1d1d1f]">
          3. 스미스 선장과 대화
        </h1>
        <p className="mt-2 text-sm text-[#6e6e73]">
          타이타닉의 선장 에드워드 존 스미스와 대화해 보세요.
        </p>
      </header>

      {/* 채팅 영역 */}
      <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-black/[0.06] bg-white shadow-sm">
        {/* 헤더 */}
        <div className="flex items-center gap-3 border-b border-black/[0.06] px-4 py-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#1e3a5f] text-lg font-bold text-white select-none">
            S
          </div>
          <div>
            <p className="text-sm font-medium text-[#1d1d1f]">Captain Edward J. Smith</p>
            <p className="text-xs text-[#86868b]">RMS Titanic · 1912</p>
          </div>
        </div>

        {/* 메시지 목록 */}
        <div
          ref={listRef}
          className="flex-1 space-y-3 overflow-y-auto px-4 py-4"
        >
          {messages.map((m, i) => (
            <div
              key={i}
              className={cn(
                "flex",
                m.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {m.role === "assistant" && (
                <div className="mr-2 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#1e3a5f] text-xs font-bold text-white self-end">
                  S
                </div>
              )}
              <div
                className={cn(
                  "max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                  m.role === "user"
                    ? "rounded-br-sm bg-black/[0.06] text-[#1d1d1f]"
                    : "rounded-bl-sm bg-[#1e3a5f] text-white shadow-sm"
                )}
              >
                {m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="mr-2 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#1e3a5f] text-xs font-bold text-white self-end">
                S
              </div>
              <div className="rounded-2xl rounded-bl-sm bg-[#1e3a5f] px-4 py-2.5 shadow-sm">
                <Loader2 className="h-4 w-4 animate-spin text-white" />
              </div>
            </div>
          )}
        </div>

        {/* 추천 질문 */}
        <div className="flex flex-wrap gap-2 border-t border-black/[0.06] px-4 py-2">
          {[
            "타이타닉은 어떤 배인가요?",
            "빙산과 충돌한 날 무슨 일이 있었나요?",
            "승객들은 어떻게 구조됐나요?",
            "타이타닉의 속도는 얼마였나요?",
          ].map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => setInput(q)}
              className="rounded-full bg-black/[0.04] px-3 py-1 text-xs text-[#1d1d1f]/70 hover:bg-black/[0.07] transition"
            >
              {q}
            </button>
          ))}
        </div>

        {/* 입력창 */}
        <div className="flex items-end gap-2 border-t border-black/[0.06] px-4 py-3">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send();
              }
            }}
            placeholder="스미스 선장에게 질문하기…"
            className="min-w-0 flex-1 resize-none rounded-xl border border-black/10 bg-[#fbfbfd] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#1e3a5f]/20"
          />
          <button
            type="button"
            onClick={() => void send()}
            disabled={!input.trim() || loading}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#1e3a5f] text-white transition hover:bg-[#162d4a] disabled:opacity-40"
          >
            <SendHorizontal className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
