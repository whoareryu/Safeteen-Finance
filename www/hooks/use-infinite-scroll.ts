"use client";

import { useEffect, useRef } from "react";

type UseInfiniteScrollOptions = {
  enabled: boolean;
  hasMore: boolean;
  loading: boolean;
  loadingMore: boolean;
  onLoadMore: () => void | Promise<void>;
  /** 뷰포트 진입 전 미리 로드 (기본 240px) */
  rootMargin?: string;
};

/**
 * sentinel ref가 보이면 onLoadMore 호출. loadingMore 중에는 재호출하지 않음.
 */
export function useInfiniteScroll({
  enabled,
  hasMore,
  loading,
  loadingMore,
  onLoadMore,
  rootMargin = "240px",
}: UseInfiniteScrollOptions) {
  const sentinelRef = useRef<HTMLDivElement>(null);
  const onLoadMoreRef = useRef(onLoadMore);
  onLoadMoreRef.current = onLoadMore;

  useEffect(() => {
    if (!enabled || !hasMore || loading || loadingMore) return;

    const el = sentinelRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          void onLoadMoreRef.current();
        }
      },
      { root: null, rootMargin, threshold: 0 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [enabled, hasMore, loading, loadingMore, rootMargin]);

  return sentinelRef;
}
