"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import RestaurantCard from "@/components/restaurant-card";
import { appendLocationParams } from "@/lib/gourmet-location";

type DailyPickData = {
  date: string;
  restaurant: {
    id: number;
    name: string;
    image_url: string;
    district: string;
    category_slug: string | null;
    category_label: string | null;
    avg_price: number | null;
    signature_menu: string;
    distance_km: number | null;
  } | null;
  daily_budget: number | null;
  budget_applied: boolean;
  message: string;
};

export default function TodayDailyPick() {
  const { user } = useAuth();
  const { coords } = useNearbyLocation();
  const [data, setData] = useState<DailyPickData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (user?.id) params.set("user_id", String(user.id));
        appendLocationParams(params, coords);
        const res = await fetch(`/api/gourmet/daily-pick?${params}`, {
          cache: "no-store",
        });
        if (!res.ok) {
          throw new Error(`불러오기 실패 (HTTP ${res.status})`);
        }
        const json = (await res.json()) as DailyPickData;
        if (!cancelled) setData(json);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "오류");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user?.id, coords?.lat, coords?.lng]);

  return (
    <section
      className="today-daily-pick w-full border-t border-black/[0.06] bg-[#f0f0f2] px-4 py-8 dark:border-white/[0.06] dark:bg-[#111] md:px-8 md:py-10"
      aria-labelledby="today-daily-pick-title"
    >
      <div className="mx-auto max-w-3xl">
        <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-amber-700">
              <Sparkles className="h-3.5 w-3.5" aria-hidden />
              Today&apos;s Pick
            </p>
            <h2
              id="today-daily-pick-title"
              className="mt-1 text-2xl font-bold tracking-tight text-[#1d1d1f] dark:text-white md:text-3xl"
            >
              오늘의 추천 맛집
            </h2>
          </div>
          {data?.date ? (
            <time className="text-sm text-[#6e6e73] dark:text-white/50" dateTime={data.date}>
              {data.date}
            </time>
          ) : null}
        </div>

        {loading ? (
          <p className="text-sm text-[#6e6e73] dark:text-white/50">오늘의 한 곳을 고르는 중…</p>
        ) : null}

        {error ? (
          <p className="text-sm text-red-600">{error}</p>
        ) : null}

        {!loading && !error && data ? (
          <>
            <p className="mb-5 text-sm leading-relaxed text-[#6e6e73] dark:text-white/50">
              {data.message}
              {data.budget_applied && data.daily_budget != null ? (
                <span className="mt-1 block font-medium text-[#1d1d1f]">
                  하루 권장 식비: {data.daily_budget.toLocaleString()}원
                  {!user ? (
                    <span className="font-normal text-[#86868b]">
                      {" "}
                      (로그인 후 버짓설정을 저장하면 매일 반영됩니다)
                    </span>
                  ) : null}
                </span>
              ) : null}
            </p>

            {data.restaurant ? (
              <div className="mx-auto max-w-sm">
                <RestaurantCard
                  restaurant={{
                    id: data.restaurant.id,
                    name: data.restaurant.name,
                    image_url: data.restaurant.image_url,
                    district: data.restaurant.district,
                    category_label: data.restaurant.category_label ?? undefined,
                    category_slug: data.restaurant.category_slug ?? undefined,
                    distance_km: data.restaurant.distance_km,
                    description:
                      data.restaurant.signature_menu ||
                      (data.restaurant.avg_price != null
                        ? `예상 1인 ${data.restaurant.avg_price.toLocaleString()}원`
                        : ""),
                  }}
                  variant="light"
                  showCategoryLabel
                  layout="grid"
                />
              </div>
            ) : (
              <p className="text-sm text-[#6e6e73]">오늘 추천할 매장이 없습니다.</p>
            )}
          </>
        ) : null}
      </div>
    </section>
  );
}
