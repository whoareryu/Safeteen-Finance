"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import type { GourmetTopic } from "@/lib/gourmet-topics";
import { appendLocationParams } from "@/lib/gourmet-location";
import TopicRowSection, { type TopicRowData } from "@/components/topic-row-section";

type HomeBrowseResponse = {
  topics: TopicRowData[];
};

type TopicBrowsePageProps = {
  topic: GourmetTopic;
};

export default function TopicBrowsePage({ topic }: TopicBrowsePageProps) {
  const { coords } = useNearbyLocation();
  const [row, setRow] = useState<TopicRowData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTopic = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.set("topic_offset", "0");
      params.set("topic_limit", "48");
      params.set("per_topic_limit", "10");
      appendLocationParams(params, coords);
      const qs = params.toString();
      const res = await fetch(
        `/api/gourmet/home-browse${qs ? `?${qs}` : ""}`,
        { cache: "no-store" }
      );
      if (!res.ok) throw new Error(`목록을 불러오지 못했습니다. (HTTP ${res.status})`);
      const data = (await res.json()) as HomeBrowseResponse;
      const match = data.topics.find((t) => t.slug === topic.slug) ?? null;
      setRow(match);
    } catch {
      setError("맛집 목록을 불러오지 못했습니다.");
      setRow(null);
    } finally {
      setLoading(false);
    }
  }, [topic.slug, coords]);

  useEffect(() => {
    void fetchTopic();
  }, [fetchTopic]);

  return (
    <main className="min-h-[calc(100dvh-var(--site-header-height))] bg-[#0d0d0d]">
      <div className="border-b border-white/10 bg-gradient-to-b from-[#1a1a1a] to-[#0d0d0d] px-4 py-8 md:px-8">
        <Link
          href="/"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-white/80 transition hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          홈
        </Link>
        <p className="text-sm text-white/60">
          <span className="mr-1" aria-hidden>
            {topic.emoji}
          </span>
          주제별 추천
        </p>
        <h1 className="mt-1 text-3xl font-bold text-white md:text-4xl">
          {topic.title}
        </h1>
        <p className="mt-2 text-base text-white/70">{topic.subtitle}</p>
      </div>

      {loading ? (
        <p className="py-20 text-center text-sm text-white/50">불러오는 중…</p>
      ) : null}

      {error ? (
        <p className="py-20 text-center text-sm text-red-400">{error}</p>
      ) : null}

      {!loading && !error && row ? (
        <div className="py-6">
          <TopicRowSection row={row} showCategoryOnCards />
        </div>
      ) : null}

      {!loading && !error && !row ? (
        <p className="py-20 text-center text-sm text-white/50">
          이 주제에 표시할 맛집이 없습니다.
        </p>
      ) : null}
    </main>
  );
}
