"use client";

import {
  Cloud,
  CloudFog,
  CloudLightning,
  CloudMoon,
  CloudRain,
  CloudSnow,
  CloudSun,
  Loader2,
  Moon,
  Sun,
  type LucideIcon,
} from "lucide-react";

const OWM_ICON_MAP: Record<string, LucideIcon> = {
  "01d": Sun,
  "01n": Moon,
  "02d": CloudSun,
  "02n": CloudMoon,
  "03d": Cloud,
  "03n": Cloud,
  "04d": Cloud,
  "04n": Cloud,
  "09d": CloudRain,
  "09n": CloudRain,
  "10d": CloudRain,
  "10n": CloudRain,
  "11d": CloudLightning,
  "11n": CloudLightning,
  "13d": CloudSnow,
  "13n": CloudSnow,
  "50d": CloudFog,
  "50n": CloudFog,
};

type WeatherIconProps = {
  code?: string;
  iconUrl?: string;
  description?: string;
  loading?: boolean;
  size?: number;
};

export default function WeatherIcon({
  code,
  iconUrl,
  description,
  loading = false,
  size = 32,
}: WeatherIconProps) {
  if (loading) {
    return (
      <span className="weather-icon-slot" aria-hidden>
        <Loader2
          className="animate-spin text-muted-foreground"
          style={{ width: size - 6, height: size - 6 }}
        />
      </span>
    );
  }

  const Fallback = (code && OWM_ICON_MAP[code]) || Cloud;

  if (iconUrl) {
    return (
      <span className="weather-icon-slot">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          className="weather-icon-img"
          src={iconUrl}
          alt={description ? `${description} 아이콘` : "날씨 아이콘"}
          width={size}
          height={size}
          onError={(e) => {
            e.currentTarget.style.display = "none";
            const fallback = e.currentTarget.nextElementSibling;
            if (fallback instanceof HTMLElement) fallback.style.display = "flex";
          }}
        />
        <span className="weather-icon-fallback" style={{ display: "none" }} aria-hidden>
          <Fallback style={{ width: size - 4, height: size - 4 }} strokeWidth={1.75} />
        </span>
      </span>
    );
  }

  if (code) {
    return (
      <span className="weather-icon-slot" aria-hidden>
        <Fallback style={{ width: size - 4, height: size - 4 }} strokeWidth={1.75} />
      </span>
    );
  }

  return null;
}
