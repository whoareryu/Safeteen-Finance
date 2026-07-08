"use client";

import { useEffect, useRef, useState } from "react";
import { loadKakaoMaps } from "@/lib/kakao-map-loader";
import { cn } from "@/lib/utils";

type KakaoMapProps = {
  latitude: number;
  longitude: number;
  /** 확대 레벨 (작을수록 확대). 기본 3. */
  level?: number;
  className?: string;
};

/** 좌표 1곳을 마커와 함께 표시하는 재사용 카카오맵. */
export default function KakaoMap({
  latitude,
  longitude,
  level = 3,
  className,
}: KakaoMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadKakaoMaps()
      .then(() => {
        if (cancelled || !containerRef.current) return;
        const center = new window.kakao.maps.LatLng(latitude, longitude);
        const map = new window.kakao.maps.Map(containerRef.current, {
          center,
          level,
        });
        new window.kakao.maps.Marker({ position: center, map });
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "지도를 불러오지 못했어요.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [latitude, longitude, level]);

  if (error) {
    return (
      <p className={cn("text-xs text-white/45", className)}>🗺️ {error}</p>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn("h-48 w-full overflow-hidden rounded-xl", className)}
    />
  );
}
