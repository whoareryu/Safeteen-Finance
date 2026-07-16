"use client";

import { useEffect, useState } from "react";
import { Bell, Droplets } from "lucide-react";
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
      <h2 className="text-xl font-semibold text-foreground">물주기 일정 &amp; 알림 이력</h2>

      {weather ? (
        <div className="saessak-card mt-3 flex items-center gap-3 px-4 py-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent text-primary">
            <Droplets className="h-5 w-5" aria-hidden />
          </span>
          <p className="text-sm text-foreground">
            {weather.region} 현재 온도 {weather.temp_c.toFixed(0)}°C · 습도{" "}
            {weather.humidity_pct.toFixed(0)}%
            {weather.is_dry_day ? " · 건조한 날씨예요 🌵" : ""}
          </p>
        </div>
      ) : null}

      {error ? (
        <p className="mt-4 rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</p>
      ) : null}

      <ul className="mt-4 space-y-3">
        {notifications.map((event) => (
          <li key={event.id} className="saessak-card flex items-start gap-3 px-4 py-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground">
              <Bell className="h-4 w-4" aria-hidden />
            </span>
            <div className="min-w-0 flex-1 text-sm">
              <p className="text-foreground">{event.message}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                채널: {event.channel} · 상태: {event.delivery_status}
              </p>
              {event.coupang_link ? (
                <a
                  href={event.coupang_link}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 inline-block text-xs font-medium text-primary"
                >
                  영양제 보러 가기
                </a>
              ) : null}
            </div>
          </li>
        ))}
        {notifications.length === 0 ? (
          <li className="text-sm text-muted-foreground">아직 발송된 알림이 없어요.</li>
        ) : null}
      </ul>
    </div>
  );
}
