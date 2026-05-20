"use client";

import { useEffect, useState } from "react";
import TopicRowSection, { type TopicRowData } from "@/components/topic-row-section";

type HomeBrowseResponse = {
  query: string | null;
  topic_count: number;
  topics: TopicRowData[];
};

type HomeTopicFeedProps = {
  query?: string;
};

export default function HomeTopicFeed({ query }: HomeTopicFeedProps) {
  const [data, setData] = useState<HomeBrowseResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (query?.trim()) params.set("q", query.trim());
        const qs = params.toString();
        const res = await fetch(
          `/api/gourmet/home-browse${qs ? `?${qs}` : ""}`,
          { cache: "no-store" }
        );
        if (!res.ok) throw new Error("목록을 불러오지 못했습니다.");
        const json = (await res.json()) as HomeBrowseResponse;
        if (!cancelled) setData(json);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "오류가 발생했습니다.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [query]);

  return (
    <section
      className="home-topic-feed w-full bg-[#0d0d0d] py-8 md:py-10"
      aria-labelledby="home-feed-title"
    >
      <h2 id="home-feed-title" className="sr-only">
        {query ? "검색 관련 주제별 맛집" : "주제별 추천 맛집"}
      </h2>

      {query ? (
        <p className="mb-6 px-4 text-center text-sm text-white/55 md:px-8">
          &quot;{query}&quot;와 관련된 주제별 추천
        </p>
      ) : null}

      {loading ? (
        <div className="flex h-40 items-center justify-center text-sm text-white/50">
          추천 맛집을 불러오는 중…
        </div>
      ) : null}

      {error ? (
        <p className="px-4 text-center text-sm text-red-400 md:px-8">{error}</p>
      ) : null}

      {!loading && !error && data?.topics.length
        ? data.topics.map((row) => (
            <TopicRowSection
              key={row.slug}
              row={row}
              showCategoryOnCards
            />
          ))
        : null}

      {!loading && !error && data?.topics.length === 0 ? (
        <p className="text-center text-sm text-white/50">표시할 추천이 없습니다.</p>
      ) : null}
    </section>
  );
}
