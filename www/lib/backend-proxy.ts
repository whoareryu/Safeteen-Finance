import { NextResponse } from "next/server";

const FORWARD_HEADERS = [
  "content-type",
  "authorization",
  "x-user-id",
  "accept",
  "accept-language",
  "cookie",
] as const;

export function getBackendBaseUrl(): string | null {
  const raw = process.env.BACKEND_URL?.trim();
  if (!raw) return null;
  return raw.replace(/\/$/, "");
}

export function backendNotConfiguredResponse() {
  return NextResponse.json(
    {
      error:
        "백엔드 URL이 설정되지 않았습니다. Vercel Environment Variables에 BACKEND_URL(공개 FastAPI 주소)을 등록한 뒤 재배포하세요.",
    },
    { status: 503 }
  );
}

/** FastAPI로 요청을 그대로 전달 (Vercel 런타임에서 BACKEND_URL 사용). */
export async function proxyToBackend(
  request: Request,
  backendPath: string
): Promise<Response> {
  const base = getBackendBaseUrl();
  if (!base) return backendNotConfiguredResponse();

  const incoming = new URL(request.url);
  const target = new URL(
    backendPath.startsWith("/") ? backendPath : `/${backendPath}`,
    base
  );
  target.search = incoming.search;

  const headers = new Headers();
  for (const name of FORWARD_HEADERS) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  let body: ArrayBuffer | undefined;
  if (request.method !== "GET" && request.method !== "HEAD") {
    body = await request.arrayBuffer();
  }

  try {
    const upstream = await fetch(target.toString(), {
      method: request.method,
      headers,
      body,
      cache: "no-store",
    });

    const outHeaders = new Headers();
    const ct = upstream.headers.get("content-type");
    if (ct) outHeaders.set("content-type", ct);

    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: outHeaders,
    });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "백엔드에 연결할 수 없습니다.";
    console.error("[backend-proxy]", target.toString(), message);
    return NextResponse.json(
      {
        error: `백엔드 연결 실패: ${message}. BACKEND_URL이 공개 URL인지 확인하세요.`,
      },
      { status: 502 }
    );
  }
}
