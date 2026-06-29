"use client";

import { ThumbsDown, ThumbsUp } from "lucide-react";
import { genreStyle } from "@/lib/genre-style";
import { cn } from "@/lib/utils";

export type GenreRestaurant = {
  name: string;
  genre: string;
  road_address: string;
  latitude: number;
  longitude: number;
};

type GenreRestaurantCardProps = {
  restaurant: GenreRestaurant;
  /** 현재 사용자 GPS 위치 (없으면 거리 미표시). */
  userLat?: number | null;
  userLng?: number | null;
  onLike?: (restaurant: GenreRestaurant) => void;
  onDislike?: (restaurant: GenreRestaurant) => void;
};

/** 두 좌표 사이 거리(m) — Haversine. */
function distanceMeters(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number,
): number {
  const R = 6371000; // 지구 반지름 (m)
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

function formatDistance(meters: number): string {
  if (meters < 1000) return `${Math.round(meters)}m`;
  return `${(meters / 1000).toFixed(1)}km`;
}

export default function GenreRestaurantCard({
  restaurant,
  userLat,
  userLng,
  onLike,
  onDislike,
}: GenreRestaurantCardProps) {
  const style = genreStyle({ label: restaurant.genre });

  const distanceLabel =
    userLat != null &&
    userLng != null &&
    Number.isFinite(restaurant.latitude) &&
    Number.isFinite(restaurant.longitude)
      ? formatDistance(
          distanceMeters(
            userLat,
            userLng,
            restaurant.latitude,
            restaurant.longitude,
          ),
        )
      : null;

  return (
    <div
      className={cn(
        "relative flex aspect-[2/3] w-full flex-col items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-b shadow-lg",
        style.gradient,
      )}
    >
      {/* 가독성용 하단 어두운 오버레이 */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/55 to-transparent" />

      {/* 우측 상단 좋아요/싫어요 */}
      <div className="absolute right-2 top-2 z-10 flex gap-1.5">
        <button
          type="button"
          aria-label="좋아요"
          onClick={() => onLike?.(restaurant)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-black/30 text-white backdrop-blur-sm transition hover:bg-black/50 active:scale-90"
        >
          <ThumbsUp className="h-4 w-4" aria-hidden />
        </button>
        <button
          type="button"
          aria-label="싫어요"
          onClick={() => onDislike?.(restaurant)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-black/30 text-white backdrop-blur-sm transition hover:bg-black/50 active:scale-90"
        >
          <ThumbsDown className="h-4 w-4" aria-hidden />
        </button>
      </div>

      {/* 중앙 이모지 */}
      <span className="z-[1] text-[64px] leading-none" aria-hidden>
        {style.emoji}
      </span>

      {/* 이름·장르 */}
      <div className="z-[1] mt-3 px-3 text-center">
        <h3 className="line-clamp-2 text-base font-bold text-white drop-shadow">
          {restaurant.name}
        </h3>
        <p className="mt-0.5 text-xs font-medium text-white/70">{restaurant.genre}</p>
      </div>

      {/* 하단 거리 */}
      {distanceLabel ? (
        <p className="absolute inset-x-0 bottom-3 z-[1] text-center text-xs font-medium text-white/90">
          📍 {distanceLabel}
        </p>
      ) : null}
    </div>
  );
}
