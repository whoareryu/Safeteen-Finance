"use client";

import Image from "next/image";
import Link from "next/link";
import { Eye, MapPin } from "lucide-react";
import FavoriteStarButton from "@/components/favorite-star-button";
import { restaurantDetailPath } from "@/lib/gourmet";
import { formatDistanceKm } from "@/lib/gourmet-location";

export type RestaurantSummary = {
  id: number;
  name: string;
  image_url: string;
  district?: string;
  description?: string;
  view_count?: number;
  rank?: number | null;
  category_label?: string | null;
  category_slug?: string | null;
  distance_km?: number | null;
  detail_href?: string | null;
};

type RestaurantCardProps = {
  restaurant: RestaurantSummary;
  variant?: "light" | "dark";
  showCategoryLabel?: boolean;
  /** 가로 스크롤 행 vs 검색 그리드 */
  layout?: "carousel" | "grid";
};

export default function RestaurantCard({
  restaurant,
  variant = "dark",
  showCategoryLabel = false,
  layout = "carousel",
}: RestaurantCardProps) {
  const isDark = variant === "dark";
  const showViews = restaurant.view_count != null && restaurant.view_count > 0;
  const distanceLabel = formatDistanceKm(restaurant.distance_km);
  const districtLine = restaurant.district?.trim() ?? "";
  const descriptionLine = restaurant.description?.trim() ?? "";
  const href = restaurant.detail_href?.trim()
    ? restaurant.detail_href
    : restaurantDetailPath(restaurant.id);

  const wrapperClass =
    isDark
      ? layout === "grid"
        ? "group relative block h-full w-full overflow-hidden rounded-md bg-[#1a1a1a] ring-1 ring-white/10 transition hover:ring-white/25"
        : "group relative block h-full w-[200px] shrink-0 overflow-hidden rounded-md bg-[#1a1a1a] ring-1 ring-white/10 transition hover:ring-white/25 sm:w-[220px]"
      : "relative block h-full overflow-hidden rounded-2xl bg-white shadow-md ring-1 ring-black/[0.06] transition hover:ring-black/15";

  return (
    <div className={wrapperClass}>
    <Link href={href} className="block h-full">
      <div className="relative aspect-[16/10] bg-[#2a2a2a]">
        <Image
          src={restaurant.image_url}
          alt={restaurant.name}
          fill
          loading="lazy"
          className="object-cover transition duration-300 group-hover:scale-105"
          sizes="220px"
        />
        {restaurant.rank != null ? (
          <span className="absolute left-2 top-2 rounded bg-black/70 px-2 py-0.5 text-[10px] font-semibold text-white">
            #{restaurant.rank}
          </span>
        ) : null}
        {showViews ? (
          <span className="absolute right-10 top-2 flex items-center gap-0.5 rounded bg-black/70 px-1.5 py-0.5 text-[10px] text-white">
            <Eye className="h-3 w-3" aria-hidden />
            {restaurant.view_count}
          </span>
        ) : null}
        <div className="absolute right-2 top-2 z-10">
          <FavoriteStarButton storeId={restaurant.id} />
        </div>
      </div>
      <div className={`p-3 ${isDark ? "text-white" : ""}`}>
        <div className="flex items-start justify-between gap-1">
          <h3
            className={`line-clamp-1 text-sm font-semibold ${isDark ? "text-white" : "text-[#1d1d1f]"}`}
          >
            {restaurant.name}
          </h3>
          {showCategoryLabel && restaurant.category_label ? (
            <span className="shrink-0 rounded bg-white/10 px-1.5 py-0.5 text-[10px] text-white/70">
              {restaurant.category_label}
            </span>
          ) : null}
        </div>
        {districtLine || distanceLabel ? (
          <p
            className={`mt-0.5 flex items-center gap-1 text-[11px] ${isDark ? "text-white/60" : "text-[#6e6e73]"}`}
          >
            <MapPin className="h-3 w-3 shrink-0" aria-hidden />
            <span>
              {districtLine}
              {distanceLabel ? (
                <span className={isDark ? "text-white/45" : "text-[#86868b]"}>
                  {districtLine ? " · " : ""}
                  {distanceLabel}
                </span>
              ) : null}
            </span>
          </p>
        ) : null}
        {descriptionLine ? (
          <p
            className={`mt-1.5 line-clamp-2 text-[11px] leading-snug ${isDark ? "text-white/55" : "text-[#6e6e73]"}`}
          >
            {descriptionLine}
          </p>
        ) : null}
      </div>
    </Link>
    </div>
  );
}
