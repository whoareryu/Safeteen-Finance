import { NextRequest, NextResponse } from "next/server";

function parseCoord(raw: string | null): number | null {
  if (raw == null || raw.trim() === "") return null;
  const n = Number(raw);
  if (!Number.isFinite(n)) return null;
  return n;
}

export async function GET(request: NextRequest) {
  const apiKey = process.env.OPENWEATHER_API_KEY?.trim();
  if (!apiKey) {
    return NextResponse.json(
      { error: "frontend/.env.local 에 OPENWEATHER_API_KEY 를 설정하세요." },
      { status: 503 }
    );
  }

  const lat = parseCoord(request.nextUrl.searchParams.get("lat"));
  const lon = parseCoord(request.nextUrl.searchParams.get("lon"));

  const url = new URL("https://api.openweathermap.org/data/2.5/weather");
  url.searchParams.set("appid", apiKey);
  url.searchParams.set("units", "metric");
  url.searchParams.set("lang", "kr");

  let locationLabel: string;

  if (lat != null && lon != null) {
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      return NextResponse.json(
        { error: "위치 좌표가 올바르지 않습니다." },
        { status: 400 }
      );
    }
    url.searchParams.set("lat", String(lat));
    url.searchParams.set("lon", String(lon));
    locationLabel = "현재 위치";
  } else {
    const city = process.env.OPENWEATHER_CITY?.trim() || "Seoul";
    url.searchParams.set("q", city);
    locationLabel = city;
  }

  let res: Response;
  try {
    res = await fetch(url.toString(), { next: { revalidate: 600 } });
  } catch {
    return NextResponse.json(
      { error: "OpenWeather API에 연결할 수 없습니다." },
      { status: 502 }
    );
  }

  let data: unknown;
  try {
    data = await res.json();
  } catch {
    return NextResponse.json(
      { error: "OpenWeather 응답을 해석할 수 없습니다." },
      { status: 502 }
    );
  }

  if (!res.ok) {
    const msg =
      typeof data === "object" &&
      data !== null &&
      "message" in data &&
      typeof (data as { message?: string }).message === "string"
        ? (data as { message: string }).message
        : "OpenWeather 요청이 실패했습니다.";
    return NextResponse.json({ error: msg }, { status: res.status === 401 ? 401 : 502 });
  }

  const w = data as {
    name?: string;
    main?: { temp?: number };
    weather?: { description?: string; icon?: string }[];
  };

  const temp = w.main?.temp;
  const description = w.weather?.[0]?.description;
  const icon = w.weather?.[0]?.icon;

  if (temp === undefined || !description || !icon) {
    return NextResponse.json(
      { error: "날씨 데이터 형식이 올바르지 않습니다." },
      { status: 502 }
    );
  }

  return NextResponse.json({
    city: w.name ?? locationLabel,
    temp: Math.round(temp),
    description,
    icon,
    iconUrl: `/api/weather/icon?code=${encodeURIComponent(icon)}`,
    locationSource: lat != null && lon != null ? "geolocation" : "city",
  });
}
