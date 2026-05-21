"use client";

import { useEffect, useState } from "react";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import RestaurantCard from "@/components/restaurant-card";
import { appendLocationParams } from "@/lib/gourmet-location";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

export type TodayPick = {
  id: number;
  name: string;
  image_url: string;
  district?: string;
  distance_km?: number | null;
  rank?: number | null;
  category_slug?: string | null;
  category_label?: string | null;
};

type TodayPicksResponse = {
  title: string;
  date: string;
  picks: TodayPick[];
  nearby_mode?: boolean;
  pagination: {
    offset: number;
    limit: number;
    total: number;
    has_more: boolean;
  };
};

function PickCard({ pick }: { pick: TodayPick }) {
  return (
    <RestaurantCard
      restaurant={{
        id: pick.id,
        name: pick.name,
        image_url: pick.image_url,
        district: pick.district,
        rank: pick.rank ?? undefined,
        category_label: pick.category_label ?? undefined,
        category_slug: pick.category_slug ?? undefined,
        distance_km: pick.distance_km,
      }}
      variant="light"
    />
  );
}

export default function TodaysPicksCarousel() {
  const { coords } = useNearbyLocation();
  const [data, setData] = useState<TodayPicksResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        appendLocationParams(params, coords);
        const qs = params.toString();
        const res = await fetch(
          `/api/gourmet/today-picks${qs ? `?${qs}` : ""}`,
          { cache: "no-store" }
        );
        if (!res.ok) throw new Error(`목록을 불러오지 못했습니다. (HTTP ${res.status})`);
        const json = (await res.json()) as TodayPicksResponse;
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
  }, [coords]);

  const picks = data?.picks ?? [];
  const sectionTitle = data?.title ?? "오늘의 맛집";

  return (
    <section className="todays-picks w-full" aria-labelledby="todays-picks-title">
      <div className="mb-5 flex items-end justify-between gap-4">
        <h2
          id="todays-picks-title"
          className="text-2xl font-semibold tracking-tight text-[#1d1d1f] md:text-3xl"
        >
          {sectionTitle}
        </h2>
        {data?.date ? (
          <p className="shrink-0 text-xs text-[#86868b]">{data.date}</p>
        ) : null}
      </div>

      {loading ? (
        <div className="flex h-[280px] items-center justify-center rounded-2xl bg-[#f5f5f7] text-sm text-[#6e6e73]">
          오늘의 맛집을 불러오는 중…
        </div>
      ) : null}

      {error ? (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-8 text-center text-sm text-red-700">
          {error}
          <p className="mt-2 text-xs text-red-600/80">
            백엔드 서버가 실행 중인지 확인해 주세요.
          </p>
        </div>
      ) : null}

      {!loading && !error && picks.length > 0 ? (
        <Carousel
          opts={{ align: "start", loop: false }}
          className="relative w-full"
        >
          <CarouselContent className="-ml-3 md:-ml-4">
            {picks.map((pick) => (
              <CarouselItem
                key={pick.id}
                className="basis-[88%] pl-3 sm:basis-[48%] md:basis-[38%] lg:basis-[30%] md:pl-4"
              >
                <PickCard pick={pick} />
              </CarouselItem>
            ))}
          </CarouselContent>
          {picks.length > 1 ? (
            <>
              <CarouselPrevious className="left-0 z-10 border-none bg-white/95 shadow-md hover:bg-white" />
              <CarouselNext className="right-0 z-10 border-none bg-white/95 shadow-md hover:bg-white" />
            </>
          ) : null}
        </Carousel>
      ) : null}

      {!loading && !error && picks.length === 0 ? (
        <p className="text-center text-sm text-[#6e6e73]">
          오늘 추천 가능한 맛집이 없습니다.
        </p>
      ) : null}
    </section>
  );
}
