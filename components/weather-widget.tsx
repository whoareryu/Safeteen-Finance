"use client";

import { useEffect, useState } from "react";
import WeatherIcon from "./weather-icon";

type WeatherData = {
  city: string;
  temp: number;
  description: string;
  icon: string;
  iconUrl: string;
  locationSource?: "geolocation" | "city";
};

function getBrowserPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (typeof navigator === "undefined" || !navigator.geolocation) {
      reject(new Error("이 브라우저는 위치 정보를 지원하지 않습니다."));
      return;
    }
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: false,
      timeout: 12_000,
      maximumAge: 300_000,
    });
  });
}

/**
 * 오늘의 날씨 (OpenWeatherMap) — 브라우저 위치 기반, 거부 시 서버 기본 도시로 폴백.
 */
export default function WeatherWidget() {
  const [data, setData] = useState<WeatherData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchWeather(lat?: number, lon?: number) {
      const qs =
        lat != null && lon != null
          ? `?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`
          : "";
      const res = await fetch(`/api/weather${qs}`);
      const body = (await res.json()) as WeatherData & { error?: string };

      if (cancelled) return;

      if (!res.ok) {
        setError(body.error ?? "날씨를 불러오지 못했습니다.");
        setData(null);
        return;
      }

      setData(body);
      setError(null);
    }

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const position = await getBrowserPosition();
        if (cancelled) return;
        await fetchWeather(position.coords.latitude, position.coords.longitude);
      } catch (geoErr) {
        if (cancelled) return;
        try {
          await fetchWeather();
        } catch {
          if (!cancelled) {
            const msg =
              geoErr instanceof Error ? geoErr.message : "위치를 확인할 수 없습니다.";
            setError(msg);
            setData(null);
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const tempText = loading
    ? "…"
    : error && !data
      ? "—"
      : data
        ? `${data.temp}°C`
        : "—";

  const descText = loading
    ? "불러오는 중"
    : data
      ? `${data.city} · ${data.description}`
      : error
        ? error.length > 32
          ? `${error.slice(0, 32)}…`
          : error
        : "";

  return (
    <div
      id="weather-container"
      role="status"
      aria-live="polite"
      aria-label={data ? `오늘의 날씨, ${data.temp}도, ${data.description}` : "오늘의 날씨"}
      className={error && !data ? "weather-error" : undefined}
    >
      <WeatherIcon
        loading={loading}
        code={data?.icon}
        iconUrl={data?.iconUrl}
        description={data?.description}
        size={36}
      />

      <div className="weather-text">
        <span id="weather-temp">{tempText}</span>
        {descText ? <span id="weather-desc">{descText}</span> : null}
      </div>
    </div>
  );
}
