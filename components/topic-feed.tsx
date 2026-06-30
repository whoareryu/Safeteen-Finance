"use client";

import { useEffect, useState } from "react";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import RestaurantMapModal from "@/components/restaurant-map-modal";
import { fetchTopicFeed, type TopicRestaurant, type TopicRow } from "@/lib/gourmet-topic-feed";
import { genreStyle } from "@/lib/genre-style";
import { cn } from "@/lib/utils";

function distanceKm(lat1: number, lng1: number, lat2: number, lng2: number) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

function formatDist(km: number) {
  return km < 1 ? `${Math.round(km * 1000)}m` : `${km.toFixed(1)}km`;
}

type MapTarget = { name: string; address: string; lat: number; lng: number };

function TopicCard({
  r,
  userLat,
  userLng,
  onMapClick,
}: {
  r: TopicRestaurant;
  userLat: number | null;
  userLng: number | null;
  onMapClick: (t: MapTarget) => void;
}) {
  const style = genreStyle({ label: r.genre });
  const dist =
    userLat != null && userLng != null && r.latitude != null && r.longitude != null
      ? formatDist(distanceKm(userLat, userLng, r.latitude, r.longitude))
      : null;

  const canMap = r.latitude != null && r.longitude != null;

  return (
    <button
      type="button"
      onClick={() =>
        canMap &&
        onMapClick({
          name: r.name,
          address: r.road_address,
          lat: r.latitude!,
          lng: r.longitude!,
        })
      }
      className={cn(
        "relative flex h-32 w-28 shrink-0 flex-col items-center justify-center overflow-hidden rounded-xl bg-gradient-to-b shadow",
        style.gradient,
        canMap && "cursor-pointer active:scale-95 transition",
      )}
    >
      <span className="text-3xl leading-none" aria-hidden>
        {style.emoji}
      </span>
      <p className="mt-1.5 line-clamp-2 px-1.5 text-center text-[11px] font-semibold leading-tight text-white drop-shadow">
        {r.name}
      </p>
      {dist && (
        <p className="mt-0.5 text-[10px] font-medium text-white/80">📍 {dist}</p>
      )}
    </button>
  );
}

export default function TopicFeed() {
  const { coords } = useNearbyLocation();
  const [rows, setRows] = useState<TopicRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [mapTarget, setMapTarget] = useState<MapTarget | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchTopicFeed(coords?.lat ?? null, coords?.lng ?? null).then((data) => {
      if (!cancelled) {
        setRows(data);
        setLoading(false);
      }
    });
    return () => { cancelled = true; };
  }, [coords?.lat, coords?.lng]);

  if (loading) {
    return (
      <div className="space-y-6 px-4 py-2">
        {[0, 1, 2].map((i) => (
          <div key={i} className="space-y-2">
            <div className="h-4 w-32 animate-pulse rounded bg-muted" />
            <div className="flex gap-3 overflow-hidden">
              {[0, 1, 2, 3].map((j) => (
                <div key={j} className="h-32 w-28 shrink-0 animate-pulse rounded-xl bg-muted" />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (rows.length === 0) return null;

  return (
    <>
      <section className="space-y-6 pb-8">
        {rows.map((row) => (
          <div key={row.slug}>
            <div className="mb-2 px-4">
              <h2 className="text-base font-bold text-foreground">
                {row.emoji} {row.title}
              </h2>
              <p className="text-xs text-muted-foreground">{row.subtitle}</p>
            </div>
            <div className="flex gap-3 overflow-x-auto px-4 pb-1 scrollbar-hide">
              {row.restaurants.map((r) => (
                <TopicCard
                  key={r.id}
                  r={r}
                  userLat={coords?.lat ?? null}
                  userLng={coords?.lng ?? null}
                  onMapClick={setMapTarget}
                />
              ))}
            </div>
          </div>
        ))}
      </section>

      {mapTarget && (
        <RestaurantMapModal
          name={mapTarget.name}
          address={mapTarget.address}
          latitude={mapTarget.lat}
          longitude={mapTarget.lng}
          onClose={() => setMapTarget(null)}
        />
      )}
    </>
  );
}
