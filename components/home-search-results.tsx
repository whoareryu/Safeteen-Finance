"use client";

import { useEffect, useState } from "react";
import RestaurantCard from "@/components/restaurant-card";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import { fetchRestaurantSearch, type RestaurantSearchResult } from "@/lib/gourmet";

type HomeSearchResultsProps = {
  query: string;
};

const PAGE_SIZE = 10;

export default function HomeSearchResults({ query }: HomeSearchResultsProps) {
  const { coords } = useNearbyLocation();
  const [data, setData] = useState<RestaurantSearchResult | null>(null);
  const [aggregated, setAggregated] = useState<RestaurantSearchResult["restaurants"]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query.trim()) {
      setData(null);
      setAggregated([]);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);
    setAggregated([]);

    (async () => {
      try {
        const result = await fetchRestaurantSearch(query, coords, {
          offset: 0,
          limit: PAGE_SIZE,
        });
        if (!cancelled) {
          setData(result);
          setAggregated(result.restaurants ?? []);
        }
      } catch {
        if (!cancelled) {
          setError("검색 결과를 불러오지 못했습니다.");
          setData(null);
          setAggregated([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [query, coords]);

  const loadMore = async () => {
    const pg = data?.pagination;
    if (!pg?.has_more || loadingMore || loading || !query.trim()) return;
    const nextOffset = pg.offset + pg.limit;
    setLoadingMore(true);
    setError(null);
    try {
      const page = await fetchRestaurantSearch(query, coords, {
        offset: nextOffset,
        limit: pg.limit || PAGE_SIZE,
      });
      setData(page);
      setAggregated((prev) => [...prev, ...(page.restaurants ?? [])]);
    } catch {
      setError("검색 결과를 불러오지 못했습니다.");
    } finally {
      setLoadingMore(false);
    }
  };

  if (!query.trim()) return null;

  const pageInfo = data?.pagination;
  const showLoadMore = Boolean(pageInfo?.has_more);

  return (
    <section
      className="home-search-results w-full bg-[#0d0d0d] px-4 py-8 md:px-8"
      aria-labelledby="search-results-title"
    >
      <div className="mx-auto max-w-6xl">
        <h2 id="search-results-title" className="text-lg font-semibold text-white md:text-xl">
          {loading ? `"${query}" 검색 중…` : data?.summary || `"${query}" 검색 결과`}
        </h2>

        {data?.matched_topics.length ? (
          <p className="mt-2 text-sm text-white/55">
            {data.matched_topics.map((t) => `${t.emoji} ${t.title}`).join(" · ")}
          </p>
        ) : null}

        {pageInfo && !loading ? (
          <p className="mt-1 text-xs text-white/45">
            {aggregated.length} / 전체 {pageInfo.total}곳 표시 중
          </p>
        ) : null}

        {error ? (
          <p className="mt-6 text-center text-sm text-red-400">{error}</p>
        ) : null}

        {loading ? (
          <div className="mt-8 flex h-32 items-center justify-center text-sm text-white/50">
            맛집을 찾는 중…
          </div>
        ) : null}

        {!loading && !error && aggregated.length ? (
          <>
            <ul className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 md:gap-4 lg:grid-cols-5">
              {aggregated.map((r) => (
                <li key={r.id} className="min-w-0">
                  <RestaurantCard
                    restaurant={r}
                    variant="dark"
                    layout="grid"
                    showCategoryLabel
                  />
                </li>
              ))}
            </ul>
            {showLoadMore ? (
              <div className="mt-8 flex justify-center">
                <button
                  type="button"
                  onClick={() => void loadMore()}
                  disabled={loadingMore}
                  className="rounded-full border border-white/20 bg-white/10 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-white/15 disabled:opacity-50"
                >
                  {loadingMore ? "불러오는 중…" : "더 보기"}
                </button>
              </div>
            ) : null}
          </>
        ) : null}

        {!loading && !error && data && aggregated.length === 0 ? (
          <p className="mt-8 text-center text-sm text-white/50">
            &quot;{query}&quot;에 맞는 맛집이 없습니다. 다른 키워드를 입력해 보세요.
          </p>
        ) : null}
      </div>
    </section>
  );
}
