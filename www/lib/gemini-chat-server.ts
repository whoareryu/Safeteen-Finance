import { NextResponse } from "next/server";

export type ChatMessage = { role: "user" | "assistant"; content: string };

export type GourmetChatBody = {
  messages?: ChatMessage[];
  model?: string;
  restaurant_id?: number | null;
  q?: string | null;
};

export async function runGeminiChat(
  body: GourmetChatBody,
  _options?: { systemPrefix?: string }
) {
  const messages = body.messages;
  if (!Array.isArray(messages) || messages.length === 0) {
    return NextResponse.json({ error: "messages 배열이 필요합니다." }, { status: 400 });
  }

  const trimmed = messages
    .filter(
      (m): m is ChatMessage =>
        m != null &&
        typeof m === "object" &&
        (m.role === "user" || m.role === "assistant") &&
        typeof m.content === "string"
    )
    .map((m) => ({ ...m, content: m.content.trim() }))
    .filter((m) => m.content.length > 0);

  if (trimmed.length === 0 || trimmed[trimmed.length - 1]!.role !== "user") {
    return NextResponse.json(
      { error: "마지막 메시지는 user여야 합니다." },
      { status: 400 }
    );
  }

  const backendUrl = (process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

  try {
    const res = await fetch(`${backendUrl}/gourmet/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: trimmed,
        restaurant_id: body.restaurant_id ?? null,
        q: body.q ?? null,
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      return NextResponse.json({ error: `백엔드 오류: ${err}` }, { status: res.status });
    }

    const data = (await res.json()) as { text: string; model: string; context_summary?: string };
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : "백엔드 연결 오류";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
