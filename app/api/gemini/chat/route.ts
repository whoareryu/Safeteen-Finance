import { NextResponse } from "next/server";

import { runGeminiChat, type GourmetChatBody } from "@/lib/gemini-chat-server";

export async function POST(request: Request) {
  let body: GourmetChatBody = {};
  try {
    body = (await request.json()) as GourmetChatBody;
  } catch {
    return NextResponse.json({ error: "JSON 본문이 올바르지 않습니다." }, { status: 400 });
  }
  return runGeminiChat(body);
}
