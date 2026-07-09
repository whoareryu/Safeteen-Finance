import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

const SYSTEM_PROMPT = `당신은 타이타닉호의 선장 에드워드 존 스미스(Edward John Smith)입니다.
1912년 4월 침몰 당시의 상황, 승객과 승무원, 항로, 빙산 충돌, 구조 작업 등 타이타닉과 관련된 모든 질문에 선장의 시점으로 답하세요.
한국어로 질문하면 한국어로, 영어로 질문하면 영어로 답하세요.
역할에 충실하되, 실제 역사적 사실을 바탕으로 답변하세요.`;

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { message?: string };
    const userMessage = (body.message ?? "").trim();
    if (!userMessage) {
      return NextResponse.json({ error: "메시지를 입력해 주세요." }, { status: 400 });
    }

    const res = await fetch(`${BACKEND_URL}/api/titanic/smith/chat`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ message: `${SYSTEM_PROMPT}\n\n사용자 질문: ${userMessage}` }),
    });

    const data = (await res.json().catch(() => ({}))) as { reply?: string };
    return NextResponse.json({ reply: data.reply ?? "" }, { status: res.status });
  } catch (e) {
    const message = e instanceof Error ? e.message : "오류가 발생했습니다.";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
