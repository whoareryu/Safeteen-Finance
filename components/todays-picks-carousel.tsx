"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { Eye, MapPin } from "lucide-react";
import { recordRestaurantView } from "@/lib/gourmet";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

export type TodayPick = {
  rank: number;
  id: number;
  name: string;
  category_slug: string;
  category_label: string;
  district: string;
  description: string;
  image_url: string;
  view_count?: number;
};

type TodayPicksResponse = {
  title: string;
  date: string;
  picks: TodayPick[];
};

function PickCard({ pick }: { pick: TodayPick }) {
  const [views, setViews] = useState(pick.view_count ?? 0);

  const handleView = async () => {
    const next = await recordRestaurantView(pick.id);
    if (next > 0) setViews(next);
  };

  return (
    <article
      role="button"
      tabIndex={0}
      onClick={handleView}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          void handleView();
        }
      }}
      className="h-full cursor-pointer overflow-hidden rounded-2xl bg-white shadow-md ring-1 ring-black/[0.06] transition hover:ring-black/15"
    >
      <div className="relative aspect-[16/10] bg-[#f5f5f7]">
        <Image
          src={pick.image_url}
          alt={pick.name}
          fill
          className="object-cover"
          sizes="(max-width: 640px) 70vw, 28vw"
        />
        <span className="absolute left-3 top-3 rounded-full bg-black/60 px-2.5 py-0.5 text-xs font-semibold text-white">
          #{pick.rank}
        </span>
        <span className="absolute right-3 top-3 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-xs text-white">
          <Eye className="h-3 w-3" aria-hidden />
          {views}
        </span>
      </div>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-[#1d1d1f]">{pick.name}</h3>
        <p className="mt-1 flex items-center gap-1 text-xs text-[#6e6e73]">
          <MapPin className="h-3 w-3 shrink-0" aria-hidden />
          {pick.district}
        </p>
        <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-[#6e6e73]">
          {pick.description}
        </p>
      </div>
    </article>
  );
}

export default function TodaysPicksCarousel() {
  const [data, setData] = useState<TodayPicksResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/gourmet/today-picks", { cache: "no-store" });
        if (!res.ok) throw new Error("목록을 불러오지 못했습니다.");
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
  }, []);

  const picks = data?.picks ?? [];

  return (
    <section className="todays-picks w-full" aria-labelledby="todays-picks-title">
      <div className="mb-5 flex items-end justify-between gap-4">
        <h2
          id="todays-picks-title"
          className="text-2xl font-semibold tracking-tight text-[#1d1d1f] md:text-3xl"
        >
          오늘의 맛집
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
