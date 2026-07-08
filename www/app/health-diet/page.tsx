"use client";

import { useState } from "react";
import GenreRestaurantCard from "@/components/genre-restaurant-card";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import { fetchDiet, type DietRestaurant } from "@/lib/gourmet-tabs";
import { cn } from "@/lib/utils";

const DIET_OPTIONS = [
  { value: "high_protein", label: "고단백" },
  { value: "low_carb", label: "저탄수" },
] as const;

export default function HealthDietPage() {
  const { coords } = useNearbyLocation();
  const [diet, setDiet] = useState("high_protein");
  const [list, setList] = useState<DietRestaurant[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (dietType: string) => {
    setDiet(dietType);
    setLoading(true);
    setError(null);
    try {
      const result = await fetchDiet(dietType);
      setList(result.restaurants);
    } catch (e) {
      setError(e instanceof Error ? e.message : "추천을 불러오지 못했어요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-md px-4 py-6 pb-24">
      <h1 className="text-xl font-bold">💪 헬스 식단</h1>
      <p className="mt-1 text-sm text-muted-foreground">식단 조건에 맞는 식당을 추천해요.</p>
      <div className="mt-4 flex gap-2">
        {DIET_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => void run(opt.value)}
            className={cn(
              "flex-1 rounded-xl py-3 text-sm font-semibold",
              diet === opt.value
                ? "bg-primary text-white"
                : "bg-muted text-foreground",
            )}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="mt-6 text-sm text-muted-foreground">추천 불러오는 중…</p>
      ) : error ? (
        <p className="mt-6 text-sm text-destructive">{error}</p>
      ) : list ? (
        list.length > 0 ? (
          <div className="mt-6 grid grid-cols-2 gap-3">
            {list.map((r) => (
              <GenreRestaurantCard
                key={r.id}
                restaurant={{
                  name: r.name,
                  genre: r.genre,
                  road_address: r.road_address,
                  latitude: r.latitude ?? 0,
                  longitude: r.longitude ?? 0,
                }}
                userLat={coords?.lat ?? null}
                userLng={coords?.lng ?? null}
              />
            ))}
          </div>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">조건에 맞는 식당이 없어요.</p>
        )
      ) : (
        <p className="mt-6 text-sm text-muted-foreground">
          식단을 선택하면 추천을 보여드려요.
        </p>
      )}
    </main>
  );
}
