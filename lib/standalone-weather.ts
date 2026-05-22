import { NextResponse } from "next/server";

export async function fetchStandaloneWeather(request: Request) {
  const apiKey = process.env.OPENWEATHER_API_KEY?.trim();
  if (!apiKey) {
    return NextResponse.json(
      {
        error:
          "OPENWEATHER_API_KEY가 없습니다. Vercel에 등록하거나 로컬 .env.local을 확인하세요.",
      },
      { status: 503 }
    );
  }

  const url = new URL(request.url);
  const lat = url.searchParams.get("lat");
  const lon = url.searchParams.get("lon");
  const city = process.env.OPENWEATHER_CITY?.trim() || "Seoul";

  const params = new URLSearchParams({
    appid: apiKey,
    units: "metric",
    lang: "kr",
  });

  let locationSource: "geolocation" | "city" = "city";
  let locationLabel = city;

  if (lat && lon) {
    params.set("lat", lat);
    params.set("lon", lon);
    locationSource = "geolocation";
    locationLabel = "현재 위치";
  } else {
    params.set("q", city);
  }

  const owUrl = `https://api.openweathermap.org/data/2.5/weather?${params}`;

  try {
    const res = await fetch(owUrl, { cache: "no-store" });
    const data = (await res.json()) as {
      name?: string;
      main?: { temp?: number };
      weather?: { description?: string; icon?: string }[];
      message?: string;
    };

    if (!res.ok) {
      return NextResponse.json(
        { error: data.message ?? "OpenWeather 요청 실패" },
        { status: 502 }
      );
    }

    const temp = data.main?.temp;
    const w0 = data.weather?.[0];
    if (temp == null || !w0?.description || !w0.icon) {
      return NextResponse.json({ error: "날씨 데이터 형식 오류" }, { status: 502 });
    }

    const icon = w0.icon;
    return NextResponse.json({
      city: data.name ?? locationLabel,
      temp: Math.round(temp),
      description: w0.description,
      icon,
      iconUrl: `/api/weather/icon?code=${encodeURIComponent(icon)}`,
      locationSource,
      mode: "standalone",
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "OpenWeather 연결 실패";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}

export function standaloneWeatherIcon(code: string) {
  const safe = code.replace(/[^0-9a-z]/gi, "").slice(0, 8);
  if (!safe) {
    return NextResponse.json({ error: "icon code 필요" }, { status: 400 });
  }
  return NextResponse.redirect(
    `https://openweathermap.org/img/wn/${safe}@2x.png`,
    302
  );
}
