import { NextResponse } from "next/server";

const ALLOWED_MODELS = new Set(["gemini-2.0-flash", "gemini-1.5-flash"]);

type ChatMessage = { role: "user" | "assistant"; content: string };

function toGeminiContents(messages: ChatMessage[]) {
  return messages.map((m) => ({
    role: m.role === "assistant" ? ("model" as const) : ("user" as const),
    parts: [{ text: m.content.slice(0, 24000) }],
  }));
}

export async function POST(request: Request) {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey?.trim()) {
    return NextResponse.json(
      { error: "서버에 GEMINI_API_KEY가 설정되지 않았습니다." },
      { status: 503 }
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "JSON 본문이 올바르지 않습니다." }, { status: 400 });
  }

  if (!body || typeof body !== "object") {
    return NextResponse.json({ error: "요청 본문이 올바르지 않습니다." }, { status: 400 });
  }

  const { messages, model: modelRaw } = body as {
    messages?: ChatMessage[];
    model?: string;
  };

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

  if (trimmed.length === 0) {
    return NextResponse.json({ error: "빈 메시지는 보낼 수 없습니다." }, { status: 400 });
  }

  if (trimmed[trimmed.length - 1]!.role !== "user") {
    return NextResponse.json(
      { error: "마지막 메시지는 사용자(user)여야 합니다." },
      { status: 400 }
    );
  }

  const model =
    typeof modelRaw === "string" && ALLOWED_MODELS.has(modelRaw)
      ? modelRaw
      : "gemini-2.0-flash";

  const recent = trimmed.slice(-20);
  const contents = toGeminiContents(recent);

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(apiKey)}`;

  let upstream: Response;
  try {
    upstream = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contents }),
    });
  } catch {
    return NextResponse.json(
      { error: "Gemini API에 연결할 수 없습니다." },
      { status: 502 }
    );
  }

  let data: unknown;
  try {
    data = await upstream.json();
  } catch {
    return NextResponse.json(
      { error: "Gemini 응답을 해석할 수 없습니다." },
      { status: 502 }
    );
  }

  if (!upstream.ok) {
    const msg =
      typeof data === "object" &&
      data !== null &&
      "error" in data &&
      typeof (data as { error?: { message?: string } }).error?.message === "string"
        ? (data as { error: { message: string } }).error.message
        : "Gemini 요청이 실패했습니다.";
    return NextResponse.json({ error: msg }, { status: upstream.status === 429 ? 429 : 502 });
  }

  const cand = (data as { candidates?: unknown[] }).candidates?.[0] as
    | { content?: { parts?: { text?: string }[] } }
    | undefined;
  const text =
    cand?.content?.parts
      ?.map((p) => (typeof p.text === "string" ? p.text : ""))
      .join("")
      .trim() ?? "";

  if (!text) {
    return NextResponse.json(
      { error: "모델이 텍스트 응답을 반환하지 않았습니다." },
      { status: 502 }
    );
  }

  return NextResponse.json({ text });
}
