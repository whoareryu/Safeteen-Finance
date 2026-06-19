"use client";

import { Search, X } from "lucide-react";

const SUGGESTIONS = ["여름", "해장", "데이트", "혼밥", "가성비", "비 오는 날"];

type GourmetNavSearchProps = {
  value: string;
  onChange: (value: string) => void;
  /** Enter 또는 검색 버튼 — 확정 검색만 실행 */
  onSubmit: () => void;
  /** X — 입력만 지우고, 이미 불러온 결과는 유지 */
  onClearInput: () => void;
  onSuggestionClick: (term: string) => void;
};

export default function GourmetNavSearch({
  value,
  onChange,
  onSubmit,
  onClearInput,
  onSuggestionClick,
}: GourmetNavSearchProps) {
  return (
    <div className="gourmet-nav-search sticky top-[var(--site-header-height)] z-40 border-b border-black/[0.06] bg-[#fbfbfd]/95 px-4 py-3 backdrop-blur-md sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <label htmlFor="gourmet-search" className="sr-only">
          맛집 검색
        </label>
        <form
          className="relative"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          <Search
            className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#86868b] dark:text-white/40"
            aria-hidden
          />
          <input
            id="gourmet-search"
            type="search"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="검색 후 Enter — 여름, 해장, 데이트…"
            className="w-full rounded-full border border-black/[0.08] bg-white py-3 pl-11 pr-11 text-sm text-[#1d1d1f] shadow-sm outline-none placeholder:text-[#86868b] focus:border-[#0071e3]/40 focus:ring-2 focus:ring-[#0071e3]/15 dark:border-white/[0.08] dark:bg-[#1a1a1a] dark:text-white dark:placeholder:text-white/35 dark:focus:border-blue-500/40 dark:focus:ring-blue-500/15"
            autoComplete="off"
            enterKeyHint="search"
          />
          {value ? (
            <button
              type="button"
              onClick={onClearInput}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1.5 text-[#86868b] transition hover:bg-black/[0.06] hover:text-[#1d1d1f] dark:text-white/40 dark:hover:bg-white/10 dark:hover:text-white"
              aria-label="검색어 입력만 지우기"
            >
              <X className="h-4 w-4" />
            </button>
          ) : null}
        </form>
        <div className="mt-2 flex flex-wrap items-center justify-center gap-1.5">
          <span className="text-xs text-[#86868b] dark:text-white/40">추천</span>
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => onSuggestionClick(s)}
              className="rounded-full border border-black/[0.06] bg-white px-2.5 py-0.5 text-xs text-[#1d1d1f]/80 transition hover:border-[#0071e3]/30 hover:bg-[#0071e3]/5 hover:text-[#0071e3] dark:border-white/[0.08] dark:bg-white/5 dark:text-white/70 dark:hover:border-blue-500/30 dark:hover:bg-blue-500/10 dark:hover:text-blue-400"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
