"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Eye,
  MapPin,
  CalendarOff,
  Clock,
  Phone,
  Instagram,
  UtensilsCrossed,
} from "lucide-react";
import {
  fetchRestaurantDetail,
  formatPrice,
  recordRestaurantView,
  type RestaurantDetail,
} from "@/lib/gourmet";
import { getCategoryBySlug } from "@/lib/navigation";
import BrowseShellLayout from "@/components/browse-shell-layout";
import FavoriteStarButton from "@/components/favorite-star-button";

type RestaurantDetailPageProps = {
  restaurantId: number;
};

export default function RestaurantDetailPage({
  restaurantId,
}: RestaurantDetailPageProps) {
  const [data, setData] = useState<RestaurantDetail | null>(null);
  const [views, setViews] = useState(0);
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
      const vc = await recordRestaurantView(restaurantId);
      if (cancelled) return;
      setViews(vc > 0 ? vc : detail.view_count);
      setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [restaurantId]);

  const category = data ? getCategoryBySlug(data.category_slug) : undefined;

  return (
    <BrowseShellLayout>
      <main className="min-h-[calc(100dvh-var(--site-header-height))] bg-[#0d0d0d] text-white">
        <div className="mx-auto max-w-3xl px-4 py-6 md:px-8 md:py-10">
          <Link
            href="/"
            className="mb-6 inline-flex items-center gap-1.5 text-sm text-white/70 transition hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            홈으로
          </Link>

          {loading ? (
            <p className="py-20 text-center text-white/50">식당 정보를 불러오는 중…</p>
          ) : null}

          {error ? (
            <p className="py-20 text-center text-red-400">{error}</p>
          ) : null}

          {data && !loading && !error ? (
            <>
              <div className="relative mb-6 aspect-[16/9] overflow-hidden rounded-xl bg-[#1a1a1a] ring-1 ring-white/10">
                <Image
                  src={data.image_url}
                  alt={data.name}
                  fill
                  className="object-cover"
                  priority
                  sizes="(max-width: 768px) 100vw, 768px"
                />
                <div className="absolute right-3 top-3 z-10">
                  <FavoriteStarButton storeId={restaurantId} size="md" />
                </div>
              </div>

              <div className="mb-2 flex flex-wrap items-center gap-2">
                {category ? (
                  <Link
                    href={category.href}
                    className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-white/90 hover:bg-white/20"
                  >
                    {category.block.emoji} {data.category_label}
                  </Link>
                ) : (
                  <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/80">
                    {data.category_label}
                  </span>
                )}
                <span className="flex items-center gap-1 text-xs text-white/55">
                  <Eye className="h-3.5 w-3.5" />
                  조회 {views}
                </span>
              </div>

              <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
                {data.name}
              </h1>

              <p className="mt-2 flex items-center gap-1.5 text-sm text-white/60">
                <MapPin className="h-4 w-4 shrink-0" />
                {data.district}
              </p>

              <p className="mt-6 text-lg leading-relaxed text-white/85">
                {data.description}
              </p>

              {data.menu_items.length > 0 ? (
                <section className="mt-8 rounded-xl bg-white/5 p-5 ring-1 ring-white/10">
                  <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-white/50">
                    <UtensilsCrossed className="h-4 w-4" />
                    메뉴 · 가격
                  </h2>
                  <ul className="mt-4 divide-y divide-white/10">
                    {data.menu_items.map((item) => (
                      <li
                        key={item.name}
                        className="flex items-start justify-between gap-4 py-3 first:pt-0 last:pb-0"
                      >
                        <div>
                          <p className="font-medium text-white">{item.name}</p>
                          {item.note ? (
                            <p className="mt-0.5 text-xs text-white/50">{item.note}</p>
                          ) : null}
                        </div>
                        <span className="shrink-0 text-sm font-semibold text-white/90">
                          {formatPrice(item.price)}
                        </span>
                      </li>
                    ))}
                  </ul>
                </section>
              ) : null}

              <section className="mt-6 rounded-xl bg-white/5 p-5 ring-1 ring-white/10">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-white/50">
                  매장 정보
                </h2>
                <ul className="mt-4 space-y-4 text-sm text-white/85">
                  <li className="flex gap-3">
                    <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-white/50" />
                    <div>
                      <p className="text-xs text-white/45">주소</p>
                      <p className="mt-0.5 leading-relaxed">{data.address}</p>
                    </div>
                  </li>
                  <li className="flex gap-3">
                    <Clock className="mt-0.5 h-4 w-4 shrink-0 text-white/50" />
                    <div>
                      <p className="text-xs text-white/45">운영 시간</p>
                      <p className="mt-0.5">{data.opening_hours}</p>
                      <p className="mt-1 flex items-center gap-1.5 text-white/60">
                        <CalendarOff className="h-3.5 w-3.5" />
                        {data.closed_weekdays_label}
                      </p>
                    </div>
                  </li>
                </ul>
              </section>

              {(data.reservation_available && (data.phone || data.instagram_url)) ||
              data.reservation_note ? (
                <section className="mt-6 rounded-xl bg-white/5 p-5 ring-1 ring-white/10">
                  <h2 className="text-sm font-semibold uppercase tracking-wider text-white/50">
                    예약 · 문의
                  </h2>
                  {data.reservation_note ? (
                    <p className="mt-2 text-sm text-white/70">{data.reservation_note}</p>
                  ) : null}
                  <div className="mt-4 flex flex-wrap gap-3">
                    {data.phone ? (
                      <a
                        href={`tel:${data.phone.replace(/-/g, "")}`}
                        className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/20"
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
                        className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/20"
                      >
                        <Instagram className="h-4 w-4" />
                        Instagram
                      </a>
                    ) : null}
                  </div>
                </section>
              ) : null}

              {category ? (
                <Link
                  href={category.href}
                  className="mt-8 inline-flex rounded-full bg-[#0071e3] px-6 py-2.5 text-sm font-medium text-white transition hover:bg-[#0077ed]"
                >
                  {data.category_label} 더보기
                </Link>
              ) : null}
            </>
          ) : null}
        </div>
      </main>
    </BrowseShellLayout>
  );
}
