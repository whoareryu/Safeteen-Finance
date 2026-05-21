"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import InfiniteScrollSentinel from "@/components/infinite-scroll-sentinel";
import TopicRowSection, { type TopicRowData } from "@/components/topic-row-section";
import { useInfiniteScroll } from "@/hooks/use-infinite-scroll";
import { appendLocationParams } from "@/lib/gourmet-location";

const TOPIC_PAGE_SIZE = 4;
const PER_TOPIC_LIMIT = 10;

type TopicBrowsePagination = {
  topic_offset: number;
  topic_limit: number;
  total_topics: number;
  per_topic_limit: number;
  has_more: boolean;
};

type HomeBrowseResponse = {
  query: string | null;
  topic_count: number;
  topics: TopicRowData[];
  nearby_mode?: boolean;
  pagination: TopicBrowsePagination;
};

type HomeTopicFeedProps = {
  query?: string;
};

function buildBrowseUrl(qs: URLSearchParams) {
  const s = qs.toString();
  return `/api/gourmet/home-browse${s ? `?${s}` : ""}`;
}

export default function HomeTopicFeed({ query }: HomeTopicFeedProps) {
  const { coords, isNearbyMode, status } = useNearbyLocation();
  const [topics, setTopics] = useState<TopicRowData[]>([]);
  const [pagination, setPagination] = useState<TopicBrowsePagination | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  /** query·coords 변경 시 중복 페이지 요청 무시용 */
  const requestGen = useRef(0);

  const loadPage = useCallback(
    async (topicOffset: number, mode: "replace" | "append") => {
      const params = new URLSearchParams();
      params.set("topic_offset", String(topicOffset));
      params.set("topic_limit", String(TOPIC_PAGE_SIZE));
      params.set("per_topic_limit", String(PER_TOPIC_LIMIT));
      if (query?.trim()) params.set("q", query.trim());
      appendLocationParams(params, coords);
      const gen = ++requestGen.current;

      const res = await fetch(buildBrowseUrl(params), { cache: "no-store" });
      if (!res.ok) {
        throw new Error(
          `목록을 불러오지 못했습니다. (HTTP ${res.status})`
        );
      }
      const json = (await res.json()) as HomeBrowseResponse;
      if (gen !== requestGen.current) return;

      setPagination(json.pagination);
      if (mode === "replace") {
        setTopics(json.topics);
      } else {
        setTopics((prev) => [...prev, ...json.topics]);
      }
    },
    [query, coords]
  );

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        await loadPage(0, "replace");
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "오류가 발생했습니다.");
          setTopics([]);
          setPagination(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [query, coords, loadPage]);

  const onLoadMore = useCallback(async () => {
    if (!pagination?.has_more || loadingMore || loading) return;
    const nextOffset = pagination.topic_offset + pagination.topic_limit;
    setLoadingMore(true);
    setError(null);
    try {
      await loadPage(nextOffset, "append");
    } catch (e) {
      setError(e instanceof Error ? e.message : "오류가 발생했습니다.");
    } finally {
      setLoadingMore(false);
    }
  }, [pagination, loadingMore, loading, loadPage]);

  const sentinelRef = useInfiniteScroll({
    enabled: !loading && !error && topics.length > 0,
    hasMore: Boolean(pagination?.has_more),
    loading,
    loadingMore,
    onLoadMore,
  });

  const feedTitle = query
    ? isNearbyMode
      ? "내 주변 · 검색 관련 주제별 맛집"
      : "검색 관련 주제별 맛집"
    : isNearbyMode
      ? "내 주변 주제별 맛집"
      : "주제별 추천 맛집";

  return (
    <section
      className="home-topic-feed w-full bg-[#0d0d0d] py-8 md:py-10"
      aria-labelledby="home-feed-title"
    >
      <h2 id="home-feed-title" className="sr-only">
        {feedTitle}
      </h2>

      {isNearbyMode ? (
        <p className="mb-4 px-4 text-center text-sm text-emerald-400/90 md:px-8">
          현재 위치 기준 가까운 순으로 추천합니다
        </p>
      ) : null}

      {status === "denied" ? (
        <p className="mb-4 px-4 text-center text-xs text-white/45 md:px-8">
          위치 권한이 없어 서울 전역 맛집을 보여 드립니다. 브라우저에서 위치를 허용하면
          주변 맛집을 우선 추천합니다.
        </p>
      ) : null}

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

      {!loading && !error && topics.length
        ? topics.map((row) => (
            <TopicRowSection
              key={row.slug}
              row={row}
              showCategoryOnCards
            />
          ))
        : null}

      {!loading && !error && topics.length === 0 ? (
        <p className="text-center text-sm text-white/50">표시할 추천이 없습니다.</p>
      ) : null}

      <InfiniteScrollSentinel
        sentinelRef={sentinelRef}
        hasMore={Boolean(pagination?.has_more)}
        loading={loading}
        loadingMore={loadingMore}
        variant="dark"
      />
    </section>
  );
}
