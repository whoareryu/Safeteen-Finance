"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ArrowLeft, Search, X } from "lucide-react";
import type { NavCategory } from "@/lib/navigation";
import RestaurantCard from "@/components/restaurant-card";

type BrowseRestaurant = {
  rank: number;
  id: number;
  name: string;
  district: string;
  description: string;
  image_url: string;
  view_count?: number;
};

type TopicRow = {
  slug: string;
  title: string;
  subtitle: string;
  emoji: string;
  keywords: string[];
  restaurants: BrowseRestaurant[];
};

type BrowseResponse = {
  category_slug: string;
  category_label: string;
  query: string | null;
  topic_count: number;
  topics: TopicRow[];
};

function TopicRowSection({ row }: { row: TopicRow }) {
  if (!row.restaurants.length) return null;

  return (
    <section className="mb-8" aria-labelledby={`topic-${row.slug}`}>
      <div className="mb-3 px-4 md:px-8">
        <h2
          id={`topic-${row.slug}`}
          className="flex items-center gap-2 text-lg font-semibold text-white md:text-xl"
        >
          <span className="text-xl" aria-hidden>
            {row.emoji}
          </span>
          {row.title}
        </h2>
        <p className="mt-0.5 text-sm text-white/55">{row.subtitle}</p>
      </div>
      <div className="scrollbar-hide flex gap-3 overflow-x-auto px-4 pb-2 md:px-8">
        {row.restaurants.map((r) => (
          <RestaurantCard
            key={`${row.slug}-${r.id}`}
            restaurant={{ ...r, rank: r.rank }}
            variant="dark"
          />
        ))}
      </div>
    </section>
  );
}

type CategoryBrowseProps = {
  category: NavCategory;
};

export default function CategoryBrowse({ category }: CategoryBrowseProps) {
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [data, setData] = useState<BrowseResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(query.trim()), 280);
    return () => window.clearTimeout(t);
  }, [query]);

  const fetchBrowse = useCallback(async () => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (debounced) params.set("q", debounced);
    const qs = params.toString();
    const url = `/api/gourmet/categories/${category.slug}/browse${qs ? `?${qs}` : ""}`;
    try {
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) throw new Error("목록을 불러오지 못했습니다.");
      const body = (await res.json()) as BrowseResponse;
      setData(body);
    } catch {
      setError("맛집 주제를 불러오지 못했습니다. 백엔드 연결을 확인해 주세요.");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [category.slug, debounced]);

  useEffect(() => {
    void fetchBrowse();
  }, [fetchBrowse]);

  const topicCount = data?.topic_count ?? 0;
  const hint = useMemo(() => {
    if (!data?.topics.length && debounced) {
      return `"${debounced}"에 맞는 주제가 없습니다. 다른 키워드를 입력해 보세요.`;
    }
    return null;
  }, [data, debounced]);

  return (
    <main className="category-browse min-h-[calc(100dvh-var(--site-header-height))] bg-[#0d0d0d]">
      {/* 히어로 */}
      <section
        className={`relative overflow-hidden bg-gradient-to-b px-4 pb-8 pt-6 md:px-8 md:pb-10 ${category.accent}`}
      >
        <div
          className="pointer-events-none absolute inset-0 opacity-30"
          aria-hidden
          style={{
            backgroundImage:
              "radial-gradient(circle at 15% 90%, white 0%, transparent 50%)",
          }}
        />
        <Link
          href="/"
          className="relative z-10 mb-6 inline-flex items-center gap-1.5 text-sm text-white/80 transition hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          홈
        </Link>
        <div className="relative z-10 max-w-3xl">
          <p className="text-sm font-medium text-white/75">
            {category.block.emoji} {category.label}
          </p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-white md:text-5xl">
            {category.title}
          </h1>
          <p className="mt-3 text-base text-white/85 md:text-lg">
            {category.description}
          </p>
        </div>
      </section>

      {/* 검색 */}
      <div className="sticky top-[var(--site-header-height)] z-40 border-b border-white/10 bg-[#0d0d0d]/95 px-4 py-4 backdrop-blur-md md:px-8">
        <label htmlFor="topic-search" className="sr-only">
          주제 검색
        </label>
        <div className="relative mx-auto max-w-xl">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40"
            aria-hidden
          />
          <input
            id="topic-search"
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="주제 검색 — 가성비, 데이트, 비 오는 날, 야장…"
            className="w-full rounded-lg border border-white/15 bg-white/10 py-2.5 pl-10 pr-10 text-sm text-white placeholder:text-white/40 outline-none ring-0 focus:border-white/35 focus:bg-white/15"
            autoComplete="off"
          />
          {query ? (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-white/50 hover:bg-white/10 hover:text-white"
              aria-label="검색어 지우기"
            >
              <X className="h-4 w-4" />
            </button>
          ) : null}
        </div>
        <p className="mx-auto mt-2 max-w-xl text-center text-xs text-white/45">
          {loading
            ? "주제를 불러오는 중…"
            : debounced
              ? `검색 결과 ${topicCount}개 주제`
              : `${topicCount}개 주제 · 가로로 스크롤해 맛집을 둘러보세요`}
        </p>
      </div>

      {/* 주제 행 */}
      <div className="py-6">
        {error ? (
          <p className="px-4 text-center text-sm text-red-400 md:px-8">{error}</p>
        ) : null}

        {hint ? (
          <p className="px-4 py-12 text-center text-sm text-white/50 md:px-8">
            {hint}
          </p>
        ) : null}

        {!loading && !error && data?.topics.length
          ? data.topics.map((row) => <TopicRowSection key={row.slug} row={row} />)
          : null}

        {loading && !data ? (
          <div className="flex h-48 items-center justify-center text-sm text-white/50">
            맛집 큐레이션을 준비하는 중…
          </div>
        ) : null}
      </div>
    </main>
  );
}
