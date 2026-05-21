"use client";

import type { RefObject } from "react";

type InfiniteScrollSentinelProps = {
  sentinelRef: RefObject<HTMLDivElement | null>;
  hasMore: boolean;
  loading: boolean;
  loadingMore: boolean;
  /** 밝은 배경(홈 검색) vs 어두운 배경(주제 피드) */
  variant?: "light" | "dark";
};

export default function InfiniteScrollSentinel({
  sentinelRef,
  hasMore,
  loading,
  loadingMore,
  variant = "dark",
}: InfiniteScrollSentinelProps) {
  if (loading || !hasMore) return null;

  const textClass =
    variant === "light" ? "text-[#6e6e73]" : "text-white/50";

  return (
    <div
      ref={sentinelRef}
      className="flex min-h-[4rem] items-center justify-center px-4 py-6"
      aria-live="polite"
    >
      {loadingMore ? (
        <span className={`text-sm ${textClass}`}>불러오는 중…</span>
      ) : (
        <span className="sr-only">추가 목록 로드 대기</span>
      )}
    </div>
  );
}
