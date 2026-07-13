"use client";

import { useEffect, useState } from "react";
import {
  fetchNotifications,
  fetchWeatherStatus,
  type NotificationEvent,
  type WeatherSnapshot,
} from "@/lib/plant-api";

export default function PlantCareCalendarList({
  plantId,
  region,
}: {
  plantId: number;
  region: string;
}) {
  const [notifications, setNotifications] = useState<NotificationEvent[]>([]);
  const [weather, setWeather] = useState<WeatherSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [notificationList, weatherStatus] = await Promise.all([
          fetchNotifications(plantId),
          fetchWeatherStatus(region).catch(() => null),
        ]);
        if (!cancelled) {
          setNotifications(notificationList);
          setWeather(weatherStatus);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "케어 일정을 불러오지 못했습니다.");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [plantId, region]);

  return (
    <div className="plant-care-calendar-list w-full max-w-none">
      <h2 className="text-xl font-semibold text-[#1d1d1f]">물주기 일정 &amp; 알림 이력</h2>

      {weather ? (
        <p className="mt-3 rounded-xl border border-black/[0.08] bg-white px-4 py-3 text-sm text-[#1d1d1f]">
          {weather.region} 현재 온도 {weather.temp_c.toFixed(0)}°C · 습도{" "}
          {weather.humidity_pct.toFixed(0)}%
          {weather.is_dry_day ? " · 건조한 날씨예요 🌵" : ""}
        </p>
      ) : null}

      {error ? (
        <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
      ) : null}

      <ul className="mt-4 space-y-3">
        {notifications.map((event) => (
          <li
            key={event.id}
            className="rounded-xl border border-black/[0.08] bg-white px-4 py-3 text-sm"
          >
            <p className="text-[#1d1d1f]">{event.message}</p>
            <p className="mt-1 text-xs text-[#86868b]">
              채널: {event.channel} · 상태: {event.delivery_status}
            </p>
            {event.coupang_link ? (
              <a
                href={event.coupang_link}
                target="_blank"
                rel="noreferrer"
                className="mt-1 inline-block text-xs text-[#0071e3]"
              >
                영양제 보러 가기
              </a>
            ) : null}
          </li>
        ))}
        {notifications.length === 0 ? (
          <li className="text-sm text-[#86868b]">아직 발송된 알림이 없어요.</li>
        ) : null}
      </ul>
    </div>
  );
}
