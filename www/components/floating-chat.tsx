"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { MessageCircle, X } from "lucide-react";
import GeminiChat from "@/components/gemini-chat";
import { Button } from "@/components/ui/button";

/**
 * 전역 우하단 AI 채팅 플로팅 버튼.
 * 식물 케어 관련 질문을 일반 채팅(/api/chat)으로 전달.
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
            <p className="text-sm font-semibold">💬 플랜트 매니저 AI</p>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="채팅 닫기"
              onClick={() => setOpen(false)}
              className="h-auto w-auto rounded-lg p-1 text-muted-foreground hover:bg-muted"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto px-3 py-3">
            <GeminiChat
              variant="apple"
              apiPath="/api/chat"
              inputPlaceholder="식물 상태나 케어가 궁금하신가요?"
            />
          </div>
        </div>
      ) : null}

      <Button
        type="button"
        variant="default"
        size="icon"
        aria-label={open ? "채팅 닫기" : "AI 채팅 열기"}
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-20 right-4 z-50 h-14 w-14 rounded-full text-white shadow-xl active:scale-95"
      >
        {open ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageCircle className="h-6 w-6" />
        )}
      </Button>
    </>
  );
}
