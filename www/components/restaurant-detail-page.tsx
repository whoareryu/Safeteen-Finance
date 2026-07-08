"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowLeft,
  MapPin,
  CalendarOff,
  Clock,
  Phone,
  Instagram,
  UtensilsCrossed,
} from "lucide-react";
import KakaoMap from "@/components/kakao-map";
import {
  fetchRestaurantDetail,
  formatPrice,
  type RestaurantDetail,
} from "@/lib/gourmet";
import BrowseShellLayout from "@/components/browse-shell-layout";
import { genreStyle } from "@/lib/genre-style";
import { cn } from "@/lib/utils";

type RestaurantDetailPageProps = {
  restaurantId: number;
};

export default function RestaurantDetailPage({
  restaurantId,
}: RestaurantDetailPageProps) {
  const [data, setData] = useState<RestaurantDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      const detail = await fetchRestaurantDetail(restaurantId);
      if (cancelled) return;
      if (!detail) {
        setError("식당 정보를 찾을 수 없습니다.");
        setLoading(false);
        return;
      }
      setData(detail);
      setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [restaurantId]);

  const heroStyle = data
    ? genreStyle({ slug: data.category_slug, label: data.category_label })
    : null;

  return (
    <BrowseShellLayout>
      <main className="min-h-[calc(100dvh-var(--site-header-height))] bg-background text-foreground">
        <div className="mx-auto max-w-3xl px-4 py-6 md:px-8 md:py-10">
          <Link
            href="/"
            className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            홈으로
          </Link>

          {loading ? (
            <p className="py-20 text-center text-muted-foreground">식당 정보를 불러오는 중…</p>
          ) : null}

          {error ? (
            <p className="py-20 text-center text-destructive">{error}</p>
          ) : null}

          {data && !loading && !error ? (
            <>
              <div
                className={cn(
                  "relative mb-6 flex aspect-[16/9] items-center justify-center overflow-hidden rounded-xl bg-gradient-to-b ring-1 ring-border",
                  heroStyle?.gradient,
                )}
              >
                <span className="text-6xl leading-none opacity-95" aria-hidden>
                  {heroStyle?.emoji}
                </span>
              </div>

              <div className="mb-2 flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-muted px-3 py-1 text-xs text-foreground">
                  {data.category_label}
                </span>
              </div>

              <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
                {data.name}
              </h1>

              <p className="mt-2 flex items-center gap-1.5 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4 shrink-0" />
                {data.district}
              </p>

              <p className="mt-6 text-lg leading-relaxed text-foreground">
                {data.description}
              </p>

              {data.menu_items.length > 0 ? (
                <section className="mt-8 rounded-xl bg-card p-5 ring-1 ring-border">
                  <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                    <UtensilsCrossed className="h-4 w-4" />
                    메뉴 · 가격
                  </h2>
                  <ul className="mt-4 divide-y divide-border">
                    {data.menu_items.map((item) => (
                      <li
                        key={item.name}
                        className="flex items-start justify-between gap-4 py-3 first:pt-0 last:pb-0"
                      >
                        <div>
                          <p className="font-medium text-foreground">{item.name}</p>
                          {item.note ? (
                            <p className="mt-0.5 text-xs text-muted-foreground">{item.note}</p>
                          ) : null}
                        </div>
                        <span className="shrink-0 text-sm font-semibold text-foreground">
                          {formatPrice(item.price)}
                        </span>
                      </li>
                    ))}
                  </ul>
                </section>
              ) : null}

              <section className="mt-6 rounded-xl bg-card p-5 ring-1 ring-border">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  매장 정보
                </h2>
                <ul className="mt-4 space-y-4 text-sm text-foreground">
                  <li className="flex gap-3">
                    <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                    <div className="min-w-0 flex-1">
                      <p className="text-xs text-muted-foreground">주소</p>
                      <p className="mt-0.5 leading-relaxed">{data.address}</p>
                      {data.latitude != null && data.longitude != null ? (
                        <KakaoMap
                          latitude={data.latitude}
                          longitude={data.longitude}
                          className="mt-3"
                        />
                      ) : null}
                    </div>
                  </li>
                  <li className="flex gap-3">
                    <Clock className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">운영 시간</p>
                      <p className="mt-0.5">{data.opening_hours}</p>
                      <p className="mt-1 flex items-center gap-1.5 text-muted-foreground">
                        <CalendarOff className="h-3.5 w-3.5" />
                        {data.closed_weekdays_label}
                      </p>
                    </div>
                  </li>
                </ul>
              </section>

              {(data.reservation_available && (data.phone || data.instagram_url)) ||
              data.reservation_note ? (
                <section className="mt-6 rounded-xl bg-card p-5 ring-1 ring-border">
                  <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                    예약 · 문의
                  </h2>
                  {data.reservation_note ? (
                    <p className="mt-2 text-sm text-muted-foreground">{data.reservation_note}</p>
                  ) : null}
                  <div className="mt-4 flex flex-wrap gap-3">
                    {data.phone ? (
                      <a
                        href={`tel:${data.phone.replace(/-/g, "")}`}
                        className="inline-flex items-center gap-2 rounded-full bg-muted px-4 py-2.5 text-sm font-medium text-foreground transition hover:bg-muted"
                      >
                        <Phone className="h-4 w-4" />
                        {data.phone}
                      </a>
                    ) : null}
                    {data.instagram_url ? (
                      <a
                        href={data.instagram_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 rounded-full bg-muted px-4 py-2.5 text-sm font-medium text-foreground transition hover:bg-muted"
                      >
                        <Instagram className="h-4 w-4" />
                        Instagram
                      </a>
                    ) : null}
                  </div>
                </section>
              ) : null}

            </>
          ) : null}
        </div>
      </main>
    </BrowseShellLayout>
  );
}
