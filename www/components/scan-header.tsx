"use client";

import { Menu, ShieldCheck, UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

type ScanHeaderProps = {
  onMenuClick?: () => void;
};

export default function ScanHeader({ onMenuClick }: ScanHeaderProps) {
  return (
    <header className="sticky top-[var(--site-header-height)] z-30 flex h-14 items-center gap-3 border-b border-slate-200 bg-white/90 px-3 backdrop-blur sm:h-16 sm:px-4 md:pl-60 md:pr-6">
      <Button
        variant="ghost"
        size="icon"
        onClick={onMenuClick}
        className="h-auto w-auto rounded-lg p-2 text-slate-500 hover:bg-slate-100 md:hidden"
        aria-label="메뉴 열기"
      >
        <Menu size={20} />
      </Button>

      <div className="flex items-center gap-2 md:hidden">
        <ShieldCheck className="h-5 w-5 text-indigo-600" aria-hidden />
        <span className="text-sm font-semibold text-slate-900">FinShield Youth</span>
      </div>

      <div className="ml-auto flex items-center gap-3">
        <span className="hidden items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 sm:inline-flex">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" aria-hidden />
          AI 보안 에이전트 가동 중
        </span>
        <button
          type="button"
          className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition hover:bg-slate-200 hover:text-slate-700"
          aria-label="프로필"
        >
          <UserCircle className="h-5 w-5" aria-hidden />
        </button>
      </div>
    </header>
  );
}
