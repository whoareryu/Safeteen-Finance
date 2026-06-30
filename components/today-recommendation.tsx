"use client";

import { useCallback, useEffect, useState } from "react";
import GenreRestaurantCard from "@/components/genre-restaurant-card";
import RestaurantMapModal from "@/components/restaurant-map-modal";
import { useAuth } from "@/components/auth-provider";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import {
  currentTimeSlot,
  fetchTodayRecommendation,
  TIME_SLOT_LABEL,
  DINING_MODE_LABEL,
  type DiningMode,
  type RecommendationCard,
  type TimeSlot,
} from "@/lib/gourmet-recommendation";
import { cn } from "@/lib/utils";
import { fetchMyPreference } from "@/lib/gourmet-onboarding";
import { setVisitTarget } from "@/lib/gourmet-visit";

/** 메인 홈 — 시간대 자동 감지 + 오늘의 추천 1곳 + 마음에 들어/안 들어 (기획서 3-2). */
export default function TodayRecommendation() {
  const { user, ready } = useAuth();
  const { coords } = useNearbyLocation();
  const [slot, setSlot] = useState<TimeSlot>("lunch");
  const [diningMode, setDiningMode] = useState<DiningMode>("dine_in");
  const [card, setCard] = useState<RecommendationCard | null>(null);
  const [excluded, setExcluded] = useState<number[]>([]);
  const [genreRanking, setGenreRanking] = useState<string[]>([]);
  const [decided, setDecided] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showMap, setShowMap] = useState(false);

  const load = useCallback(async (
    excludedIds: number[],
    ranking: string[],
    lat: number | null,
    lng: number | null,
    mode: DiningMode,
  ) => {
    setLoading(true);
    setError(null);
    setDecided(false);
    const nextSlot = currentTimeSlot();
    setSlot(nextSlot);
    setShowMap(false);
    try {
      const next = await fetchTodayRecommendation({
        time_slot: nextSlot,
        excluded_ids: excludedIds,
        genre_ranking: ranking,
        lat,
        lng,
        dining_mode: mode,
      });
      setCard(next);
      if (next && next.latitude != null && next.longitude != null) {
        setVisitTarget({
          id: next.id,
          name: next.name,
          genre: next.genre,
          latitude: next.latitude,
          longitude: next.longitude,
        });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "추천을 불러오지 못했어요.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!ready || !user) return;
    let cancelled = false;
    (async () => {
      let ranking: string[] = [];
      try {
        const pref = await fetchMyPreference(user.id);
        ranking = pref.genre_ranking ?? [];
      } catch {
        /* 취향 조회 실패 시 기본(빈 순위) 추천 */
      }
      if (cancelled) return;
      setGenreRanking(ranking);
      void load([], ranking, coords?.lat ?? null, coords?.lng ?? null, diningMode);
    })();
    return () => {
      cancelled = true;
    };
  }, [ready, user, load]);

  const handleLike = useCallback(() => {
    // 좋아요: 오늘 추천 확정 (학습 신호 저장은 다음 단계에서 연동)
    setDecided(true);
  }, []);

  const handleDiningMode = useCallback((mode: DiningMode) => {
    setDiningMode(mode);
    setExcluded([]);
    void load([], genreRanking, coords?.lat ?? null, coords?.lng ?? null, mode);
  }, [coords, genreRanking, load]);

  const handleDislike = useCallback(() => {
    if (!card) return;
    const next = [...excluded, card.id];
    setExcluded(next);
    void load(next, genreRanking, coords?.lat ?? null, coords?.lng ?? null, diningMode);
  }, [card, coords, diningMode, excluded, genreRanking, load]);

  if (ready && !user) {
    return null;
  }

  return (
    <section className="mx-auto w-full max-w-sm px-4 py-6">
      <div className="mb-3 flex items-center justify-between gap-2">
        <h2 className="text-lg font-bold">{TIME_SLOT_LABEL[slot]}</h2>
        {user && (
          <div className="flex gap-1">
            {(Object.keys(DINING_MODE_LABEL) as DiningMode[]).map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => handleDiningMode(mode)}
                className={cn(
                  "rounded-full px-2.5 py-1 text-xs font-medium transition",
                  diningMode === mode
                    ? "bg-primary text-white"
                    : "bg-muted text-muted-foreground",
                )}
              >
                {DINING_MODE_LABEL[mode]}
              </button>
            ))}
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex aspect-[2/3] w-full animate-pulse items-center justify-center rounded-2xl bg-muted text-sm text-muted-foreground">
          추천 불러오는 중…
        </div>
      ) : error ? (
        <p className="text-sm text-destructive">{error}</p>
      ) : card ? (
        <>
          <GenreRestaurantCard
            restaurant={{
              name: card.name,
              genre: card.genre,
              road_address: card.road_address,
              latitude: card.latitude ?? 0,
              longitude: card.longitude ?? 0,
            }}
            userLat={coords?.lat ?? null}
            userLng={coords?.lng ?? null}
            onLike={handleLike}
            onDislike={handleDislike}
            onClick={
              card.latitude != null && card.longitude != null
                ? () => setShowMap(true)
                : undefined
            }
          />
          {showMap && card.latitude != null && card.longitude != null && (
            <RestaurantMapModal
              name={card.name}
              address={card.road_address}
              latitude={card.latitude}
              longitude={card.longitude}
              onClose={() => setShowMap(false)}
            />
          )}
          <p className="mt-2 text-center text-sm text-muted-foreground">{card.reason}</p>
          {decided ? (
            <div className="mt-3 flex flex-col items-center gap-2">
              <p className="text-sm font-semibold text-primary">
                ✅ 오늘은 여기로 정했어요!
              </p>
              <button
                type="button"
                onClick={() => void load(excluded, genreRanking, coords?.lat ?? null, coords?.lng ?? null, diningMode)}
                className="rounded-xl bg-muted px-4 py-2 text-sm font-semibold text-foreground transition active:scale-95"
              >
                다시 고르기
              </button>
            </div>
          ) : (
            <div className="mt-3 flex gap-2">
              <button
                type="button"
                onClick={handleLike}
                className="flex-1 rounded-xl bg-primary py-2.5 text-sm font-semibold text-white transition active:scale-95"
              >
                😊 마음에 들어
              </button>
              <button
                type="button"
                onClick={handleDislike}
                className="flex-1 rounded-xl bg-muted py-2.5 text-sm font-semibold text-foreground transition active:scale-95"
              >
                😞 마음에 안 들어
              </button>
            </div>
          )}
        </>
      ) : (
        <p className="text-sm text-muted-foreground">
          추천할 식당이 없어요. 잠시 후 다시 시도해 주세요.
        </p>
      )}
    </section>
  );
}
