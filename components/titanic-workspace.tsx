"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import GeminiChat from "@/components/gemini-chat";
import TitanicDataUpload from "@/components/titanic-data-upload";

type Panel = "chat" | "upload";

export default function TitanicWorkspace() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [panel, setPanel] = useState<Panel>("chat");

  return (
    <div className="titanic-workspace border-t border-black/[0.06] bg-[#fbfbfd]">
      <div className="mx-auto flex w-full max-w-6xl flex-col md:min-h-[520px] md:flex-row">
        <aside
          className="w-full shrink-0 border-b border-black/[0.06] bg-[#f5f5f7] md:w-56 md:border-b-0 md:border-r lg:w-64"
          aria-label="타이타닉 작업 메뉴"
        >
          <p className="px-3 pt-5 text-xs font-medium uppercase tracking-[0.18em] text-[#86868b]">
            파이프라인
          </p>
          <nav className="px-3 pb-4 pt-2 md:pb-6">
            <button
              type="button"
              onClick={() => setMenuOpen((o) => !o)}
              className="flex w-full items-center justify-between rounded-lg py-2.5 text-left text-sm font-medium text-[#1d1d1f] transition hover:bg-black/[0.05]"
              aria-expanded={menuOpen}
            >
              <span>데이터 · 모델</span>
              <ChevronRight
                className={cn(
                  "h-4 w-4 shrink-0 text-[#86868b] transition-transform duration-200",
                  menuOpen && "rotate-90"
                )}
                aria-hidden
              />
            </button>
            {menuOpen ? (
              <ul className="mt-0.5 space-y-0.5">
                <li>
                  <button
                    type="button"
                    onClick={() => setPanel("upload")}
                    className={cn(
                      "w-full rounded-md py-2 text-left text-sm transition",
                      panel === "upload"
                        ? "bg-white font-medium text-[#0071e3] shadow-sm ring-1 ring-black/[0.06]"
                        : "text-[#6e6e73] hover:bg-white/80 hover:text-[#1d1d1f]"
                    )}
                  >
                    1. 데이터 수집
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => setPanel("chat")}
                    className={cn(
                      "w-full rounded-md py-2 text-left text-sm transition",
                      panel === "chat"
                        ? "bg-white font-medium text-[#0071e3] shadow-sm ring-1 ring-black/[0.06]"
                        : "text-[#6e6e73] hover:bg-white/80 hover:text-[#1d1d1f]"
                    )}
                  >
                    2. Gemini 분석
                  </button>
                </li>
              </ul>
            ) : null}
          </nav>
        </aside>

        <div className="min-w-0 flex-1 px-4 py-8 sm:px-6 md:py-10">
          {panel === "upload" ? (
            <TitanicDataUpload />
          ) : (
            <div className="mx-auto w-full max-w-3xl">
              <p className="mb-5 text-center text-xs font-medium uppercase tracking-[0.2em] text-[#86868b]">
                Titanic · Gemini
              </p>
              <p className="mb-4 text-center text-sm text-[#6e6e73]">
                Neon DB 또는 CSV 기반 통계·샘플로 답합니다. 데이터 수집 후 질문해
                보세요.
              </p>
              <GeminiChat
                variant="apple"
                apiPath="/api/titanic/chat"
                inputPlaceholder="승객 수, 생존률, 객실 등급 등을 물어보기"
              />
            </div>
          )}
        </div>
      </div>

      <div className="border-t border-black/[0.06] px-6 py-8 text-center">
        <Link
          href="/portfolio"
          className="apple-cta-primary inline-flex rounded-full px-6 py-2.5 text-sm"
        >
          수업용으로
        </Link>
      </div>
    </div>
  );
}
