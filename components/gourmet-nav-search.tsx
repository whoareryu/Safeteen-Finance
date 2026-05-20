"use client";

import { Search, X } from "lucide-react";

const SUGGESTIONS = ["여름", "해장", "데이트", "혼밥", "가성비", "비 오는 날"];

type GourmetNavSearchProps = {
  value: string;
  onChange: (value: string) => void;
};

export default function GourmetNavSearch({ value, onChange }: GourmetNavSearchProps) {
  return (
    <div className="gourmet-nav-search sticky top-[var(--site-header-height)] z-40 border-b border-black/[0.06] bg-[#fbfbfd]/95 px-4 py-3 backdrop-blur-md sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <label htmlFor="gourmet-search" className="sr-only">
          맛집 검색
        </label>
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#86868b]"
            aria-hidden
          />
          <input
            id="gourmet-search"
            type="search"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="메뉴·분위기·상황으로 검색 — 여름, 해장, 데이트…"
            className="w-full rounded-full border border-black/[0.08] bg-white py-3 pl-11 pr-11 text-sm text-[#1d1d1f] shadow-sm outline-none placeholder:text-[#86868b] focus:border-[#0071e3]/40 focus:ring-2 focus:ring-[#0071e3]/15"
            autoComplete="off"
          />
          {value ? (
            <button
              type="button"
              onClick={() => onChange("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1.5 text-[#86868b] transition hover:bg-black/[0.06] hover:text-[#1d1d1f]"
              aria-label="검색어 지우기"
            >
              <X className="h-4 w-4" />
            </button>
          ) : null}
        </div>
        <div className="mt-2 flex flex-wrap items-center justify-center gap-1.5">
          <span className="text-xs text-[#86868b]">추천</span>
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => onChange(s)}
              className="rounded-full border border-black/[0.06] bg-white px-2.5 py-0.5 text-xs text-[#1d1d1f]/80 transition hover:border-[#0071e3]/30 hover:bg-[#0071e3]/5 hover:text-[#0071e3]"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
