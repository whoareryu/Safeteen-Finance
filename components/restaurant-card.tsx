"use client";

import Image from "next/image";
import { useState } from "react";
import { Eye, MapPin } from "lucide-react";
import { recordRestaurantView } from "@/lib/gourmet";

export type RestaurantSummary = {
  id: number;
  name: string;
  district: string;
  description: string;
  image_url: string;
  view_count?: number;
  rank?: number;
};

type RestaurantCardProps = {
  restaurant: RestaurantSummary;
  variant?: "light" | "dark";
};

export default function RestaurantCard({
  restaurant,
  variant = "dark",
}: RestaurantCardProps) {
  const [views, setViews] = useState(restaurant.view_count ?? 0);
  const isDark = variant === "dark";

  const handleView = async () => {
    const next = await recordRestaurantView(restaurant.id);
    if (next > 0) setViews(next);
  };

  return (
    <article
      role="button"
      tabIndex={0}
      onClick={() => void handleView()}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          void handleView();
        }
      }}
      className={
        isDark
          ? "group h-full w-[200px] shrink-0 cursor-pointer overflow-hidden rounded-md bg-[#1a1a1a] ring-1 ring-white/10 transition hover:ring-white/25 sm:w-[220px]"
          : "h-full cursor-pointer overflow-hidden rounded-2xl bg-white shadow-md ring-1 ring-black/[0.06] transition hover:ring-black/15"
      }
    >
      <div className="relative aspect-[16/10] bg-[#2a2a2a]">
        <Image
          src={restaurant.image_url}
          alt={restaurant.name}
          fill
          className="object-cover transition duration-300 group-hover:scale-105"
          sizes="220px"
        />
        {restaurant.rank != null ? (
          <span className="absolute left-2 top-2 rounded bg-black/70 px-2 py-0.5 text-[10px] font-semibold text-white">
            #{restaurant.rank}
          </span>
        ) : null}
        <span className="absolute right-2 top-2 flex items-center gap-0.5 rounded bg-black/70 px-1.5 py-0.5 text-[10px] text-white">
          <Eye className="h-3 w-3" aria-hidden />
          {views}
        </span>
      </div>
      <div className={`p-3 ${isDark ? "text-white" : ""}`}>
        <h3
          className={`line-clamp-1 text-sm font-semibold ${isDark ? "text-white" : "text-[#1d1d1f]"}`}
        >
          {restaurant.name}
        </h3>
        <p
          className={`mt-0.5 flex items-center gap-1 text-[11px] ${isDark ? "text-white/60" : "text-[#6e6e73]"}`}
        >
          <MapPin className="h-3 w-3 shrink-0" aria-hidden />
          {restaurant.district}
        </p>
        <p
          className={`mt-1.5 line-clamp-2 text-[11px] leading-snug ${isDark ? "text-white/55" : "text-[#6e6e73]"}`}
        >
          {restaurant.description}
        </p>
      </div>
    </article>
  );
}
