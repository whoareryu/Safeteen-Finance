import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

const ALLOWED_MODELS = new Set([
  "gemini-2.5-flash",
  "gemini-2.0-flash",
  "gemini-1.5-flash",
]);

export type ChatMessage = { role: "user" | "assistant"; content: string };

function toGeminiContents(messages: ChatMessage[]) {
  return messages.map((m) => ({
    role: m.role === "assistant" ? ("model" as const) : ("user" as const),
    parts: [{ text: m.content.slice(0, 24000) }],
  }));
}

export type GourmetChatBody = {
  messages?: ChatMessage[];
  model?: string;
  restaurant_id?: number | null;
  q?: string | null;
};

export async function runGeminiChat(
  body: GourmetChatBody,
  options?: { systemPrefix?: string }
) {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey?.trim()) {
    return NextResponse.json(
      { error: "GEMINI_API_KEY가 설정되지 않았습니다. (Vercel Environment Variables)" },
      { status: 503 }
    );
  }

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

  const modelName =
    typeof body.model === "string" && ALLOWED_MODELS.has(body.model)
      ? body.model
      : "gemini-2.0-flash";

  const contextBits: string[] = [];
  if (options?.systemPrefix) contextBits.push(options.systemPrefix);
  if (body.q?.trim()) contextBits.push(`검색 맥락: ${body.q.trim()}`);
  if (body.restaurant_id != null) {
    contextBits.push(`선택 매장 ID: ${body.restaurant_id} (DB 미연결 — 일반 조언만)`);
  }
  const system = [
    "당신은 서울 맛집 앱 GourmetMate의 AI 가이드입니다.",
    "확실하지 않은 매장 정보는 지어내지 말고, 일반적인 조언을 하세요.",
    ...contextBits,
  ].join("\n");

  const contents = [
    { role: "user" as const, parts: [{ text: system }] },
    {
      role: "model" as const,
      parts: [{ text: "네, 서울 맛집 가이드로서 도와드리겠습니다." }],
    },
    ...toGeminiContents(trimmed.slice(-20)),
  ];

  try {
    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: modelName });
    const result = await model.generateContent({ contents });
    const text = result.response.text().trim();
    if (!text) {
      return NextResponse.json({ error: "빈 응답입니다." }, { status: 502 });
    }
    return NextResponse.json({
      text,
      model: modelName,
      context_summary: "standalone (Vercel API, 백엔드 미사용)",
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Gemini 오류";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
