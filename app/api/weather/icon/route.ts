import { NextRequest, NextResponse } from "next/server";

const ICON_CODE = /^\d{2}[dn]$/;

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code")?.trim();
  if (!code || !ICON_CODE.test(code)) {
    return NextResponse.json({ error: "유효하지 않은 아이콘 코드입니다." }, { status: 400 });
  }

  let res: Response;
  try {
    res = await fetch(`https://openweathermap.org/img/wn/${code}@2x.png`, {
      next: { revalidate: 86400 },
    });
  } catch {
    return NextResponse.json(
      { error: "날씨 아이콘을 불러올 수 없습니다." },
      { status: 502 }
    );
  }

  if (!res.ok) {
    return NextResponse.json({ error: "날씨 아이콘을 찾을 수 없습니다." }, { status: 404 });
  }

  const body = await res.arrayBuffer();
  return new NextResponse(body, {
    headers: {
      "Content-Type": res.headers.get("Content-Type") ?? "image/png",
      "Cache-Control": "public, max-age=86400, stale-while-revalidate=3600",
    },
  });
}
