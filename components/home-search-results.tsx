"use client";

import { useEffect, useState } from "react";
import RestaurantCard from "@/components/restaurant-card";
import { fetchRestaurantSearch, type RestaurantSearchResult } from "@/lib/gourmet";

type HomeSearchResultsProps = {
  query: string;
};

export default function HomeSearchResults({ query }: HomeSearchResultsProps) {
  const [data, setData] = useState<RestaurantSearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query.trim()) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    (async () => {
      try {
        const result = await fetchRestaurantSearch(query);
        if (!cancelled) setData(result);
      } catch {
        if (!cancelled) {
          setError("검색 결과를 불러오지 못했습니다.");
          setData(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [query]);

  if (!query.trim()) return null;

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

        {error ? (
          <p className="mt-6 text-center text-sm text-red-400">{error}</p>
        ) : null}

        {loading ? (
          <div className="mt-8 flex h-32 items-center justify-center text-sm text-white/50">
            맛집을 찾는 중…
          </div>
        ) : null}

        {!loading && !error && data?.restaurants.length ? (
          <ul className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 md:gap-4 lg:grid-cols-5">
            {data.restaurants.map((r) => (
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
        ) : null}

        {!loading && !error && data && data.restaurants.length === 0 ? (
          <p className="mt-8 text-center text-sm text-white/50">
            &quot;{query}&quot;에 맞는 맛집이 없습니다. 다른 키워드를 입력해 보세요.
          </p>
        ) : null}
      </div>
    </section>
  );
}
