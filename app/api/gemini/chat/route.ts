import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

const ALLOWED_MODELS = new Set([
  "gemini-2.5-flash",
  "gemini-2.0-flash",
  "gemini-1.5-flash",
]);

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

  const modelName =
    typeof modelRaw === "string" && ALLOWED_MODELS.has(modelRaw)
      ? modelRaw
      : "gemini-2.0-flash";

  const contents = toGeminiContents(trimmed.slice(-20));

  try {
    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: modelName });
    const result = await model.generateContent({ contents });
    const text = result.response.text().trim();

    if (!text) {
      return NextResponse.json(
        { error: "모델이 텍스트 응답을 반환하지 않았습니다." },
        { status: 502 }
      );
    }

    return NextResponse.json({ text, model: modelName });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Gemini 요청이 실패했습니다.";
    console.error("[gemini/chat]", message);
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
