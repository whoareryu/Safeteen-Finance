"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { MessageCircle, X } from "lucide-react";
import GeminiChat from "@/components/gemini-chat";

/**
 * 전역 우하단 AI 채팅 플로팅 버튼 (기획서 3-3).
 * 상황 입력("오늘 친구랑 먹을거야" 등)을 맛집 RAG(/api/gourmet/chat)로 전달.
 * 채팅을 닫아도 메인 홈 추천은 그대로 유지(패널만 숨김).
 * 수업 영역(/portfolio)에서는 노출하지 않는다.
 */
export default function FloatingChat() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  if (pathname.startsWith("/portfolio")) return null;

  return (
    <>
      {open ? (
        <div className="fixed bottom-36 right-4 z-50 flex h-[60vh] max-h-[520px] w-[360px] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl bg-card shadow-2xl ring-1 ring-border">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <p className="text-sm font-semibold">💬 GourmetMate AI</p>
            <button
              type="button"
              aria-label="채팅 닫기"
              onClick={() => setOpen(false)}
              className="rounded-lg p-1 text-muted-foreground transition hover:bg-muted"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto px-3 py-3">
            <GeminiChat
              variant="apple"
              apiPath="/api/gourmet/chat"
              inputPlaceholder="오늘 어떤 상황이세요? (예: 친구랑 매운거)"
            />
          </div>
        </div>
      ) : null}

      <button
        type="button"
        aria-label={open ? "채팅 닫기" : "AI 채팅 열기"}
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-20 right-4 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-xl transition hover:bg-primary/90 active:scale-95"
      >
        {open ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageCircle className="h-6 w-6" />
        )}
      </button>
    </>
  );
}
