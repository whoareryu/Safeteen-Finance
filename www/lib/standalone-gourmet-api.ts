import { NextResponse } from "next/server";

import { runGeminiChat, type GourmetChatBody } from "@/lib/gemini-chat-server";
import {
  filterTopicsByQuery,
  mockRestaurantsForTopic,
  type MockTopicDef,
} from "@/lib/standalone-mock-data";

export function useStandaloneApi(): boolean {
  if (process.env.STANDALONE_API === "true" || process.env.STANDALONE_API === "1") {
    return true;
  }
  const backend = process.env.BACKEND_URL?.trim();
  return !backend;
}

function parseIntParam(
  searchParams: URLSearchParams,
  key: string,
  fallback: number
): number {
  const raw = searchParams.get(key);
  const n = raw ? Number.parseInt(raw, 10) : fallback;
  return Number.isFinite(n) && n >= 0 ? n : fallback;
}

export function handleStandaloneHomeBrowse(request: Request) {
  const sp = new URL(request.url).searchParams;
  const topicOffset = parseIntParam(sp, "topic_offset", 0);
  const topicLimit = Math.min(parseIntParam(sp, "topic_limit", 4), 8);
  const perTopicLimit = Math.min(parseIntParam(sp, "per_topic_limit", 10), 12);
  const q = sp.get("q");

  const all = filterTopicsByQuery(q);
  const slice = all.slice(topicOffset, topicOffset + topicLimit);

  const topics = slice.map((t: MockTopicDef) => ({
    slug: t.slug,
    title: t.title,
    subtitle: t.subtitle,
    emoji: t.emoji,
    keywords: t.keywords,
    category_slug: t.category_slug ?? null,
    category_label: t.category_label ?? null,
    link_title: true,
    restaurants: mockRestaurantsForTopic(t, perTopicLimit),
  }));

  return NextResponse.json({
    query: q?.trim() || null,
    topic_count: all.length,
    topics,
    nearby_mode: Boolean(sp.get("lat") && sp.get("lng")),
    pagination: {
      topic_offset: topicOffset,
      topic_limit: topicLimit,
      total_topics: all.length,
      per_topic_limit: perTopicLimit,
      has_more: topicOffset + topicLimit < all.length,
    },
    mode: "standalone",
    notice: "백엔드 미연결 — 목 데이터로 표시 중입니다.",
  });
}

export function handleStandaloneDailyPick(request: Request) {
  const today = new Date().toISOString().slice(0, 10);
  const topic = filterTopicsByQuery(null)[0]!;
  const [restaurant] = mockRestaurantsForTopic(topic, 1);

  return NextResponse.json({
    date: today,
    restaurant: {
      ...restaurant,
      avg_price: 15000,
      signature_menu: "대표 메뉴 (목 데이터)",
      category_slug: "hansik",
      category_label: "한식",
    },
    daily_budget: null,
    budget_applied: false,
    message: "standalone 모드 — 오늘의 한 끼 (목 데이터)",
    mode: "standalone",
  });
}

export async function handleStandaloneGourmetPath(
  request: Request,
  segment: string
) {
  const path = segment.toLowerCase();

  if (path === "home-browse" && request.method === "GET") {
    return handleStandaloneHomeBrowse(request);
  }

  if (path === "daily-pick" && request.method === "GET") {
    return handleStandaloneDailyPick(request);
  }

  if (path === "chat" && request.method === "POST") {
    let body: GourmetChatBody = {};
    try {
      body = (await request.json()) as GourmetChatBody;
    } catch {
      return NextResponse.json({ error: "JSON 오류" }, { status: 400 });
    }
    return runGeminiChat(body, {
      systemPrefix:
        "[standalone] Neon DB·실제 매장 데이터는 연결되지 않았습니다.",
    });
  }

  return NextResponse.json(
    {
      error: `standalone 모드: /gourmet/${segment} 은 지원하지 않습니다. BACKEND_URL을 설정하면 전체 API를 사용할 수 있습니다.`,
      mode: "standalone",
    },
    { status: 501 }
  );
}
