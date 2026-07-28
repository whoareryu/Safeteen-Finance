"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Bot, Loader2, SendHorizontal, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

type Msg = { role: "user" | "assistant"; content: string };

const INITIAL: Msg = {
  role: "assistant",
  content: "안녕하세요! LangChain 기반 AI 어시스턴트입니다.\n무엇이든 편하게 물어보세요.",
};

const SUGGESTIONS = [
  "너는 뭘 할 수 있어?",
  "이 프로젝트는 어떤 구조로 되어 있어?",
  "LangChain은 어떤 상황에 쓰면 좋아?",
  "간단한 자기소개를 해줘",
];

export default function LangchainChatPage() {
  const [messages, setMessages] = useState<Msg[]>([INITIAL]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = useCallback(
    async (preset?: string) => {
      const text = (preset ?? input).trim();
      if (!text || loading) return;
      setInput("");
      setLoading(true);
      setMessages((prev) => [...prev, { role: "user", content: text }]);

      try {
        const res = await fetch("/api/silicon-valley/langchain/chat", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        const data = (await res.json().catch(() => ({}))) as { reply?: string };
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply || "응답을 받지 못했습니다." },
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
    },
    [input, loading]
  );

  return (
    <div className="mx-auto flex h-[calc(100dvh-var(--site-header-height)-4rem)] max-w-3xl flex-col gap-4 px-4 py-10 md:px-8">
      <header className="pt-1">
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-foreground">
          채팅
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          LangChain으로 구현된 AI 어시스턴트와 대화해 보세요.
        </p>
      </header>

      {/* 채팅 영역 */}
      <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
        {/* 헤더 */}
        <div className="flex items-center gap-3 border-b border-border px-4 py-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">LangChain 어시스턴트</p>
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              로컬 Ollama 모델과 실시간 대화
            </p>
          </div>
        </div>

        {/* 메시지 목록 */}
        <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
          {messages.map((m, i) => (
            <div key={i} className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}>
              {m.role === "assistant" && (
                <div className="mr-2 flex h-7 w-7 shrink-0 items-center justify-center self-end rounded-full bg-muted text-muted-foreground">
                  <Bot className="h-3.5 w-3.5" />
                </div>
              )}
              <div
                className={cn(
                  "max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                  m.role === "user"
                    ? "rounded-br-sm bg-primary text-primary-foreground"
                    : "rounded-bl-sm bg-muted text-foreground shadow-sm"
                )}
              >
                {m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="mr-2 flex h-7 w-7 shrink-0 items-center justify-center self-end rounded-full bg-muted text-muted-foreground">
                <Bot className="h-3.5 w-3.5" />
              </div>
              <div className="rounded-2xl rounded-bl-sm bg-muted px-4 py-2.5 shadow-sm">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              </div>
            </div>
          )}
        </div>

        {/* 추천 질문 */}
        <div className="flex flex-wrap gap-2 border-t border-border px-4 py-2">
          {SUGGESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => void send(q)}
              disabled={loading}
              className="rounded-full bg-muted px-3 py-1 text-xs text-foreground/70 transition hover:bg-muted/70 disabled:opacity-40"
            >
              {q}
            </button>
          ))}
        </div>

        {/* 입력창 */}
        <div className="flex items-end gap-2 border-t border-border px-4 py-3">
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
            placeholder="LangChain 어시스턴트에게 질문하기…"
            className="min-w-0 flex-1 resize-none rounded-xl border border-border bg-input px-3 py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/20"
          />
          <button
            type="button"
            onClick={() => void send()}
            disabled={!input.trim() || loading}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground transition hover:opacity-90 disabled:opacity-40"
          >
            <SendHorizontal className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
