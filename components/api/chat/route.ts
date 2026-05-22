import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    // 1. 클라이언트가 보낸 메시지 가져오기
    const { prompt } = await request.json();

    // 2. 서버 환경변수에서 API 키 읽기 (브라우저에 노출되지 않음)
    const apiKey = process.env.GEMINI_API_KEY;
    
    if (!apiKey) {
      return NextResponse.json({ error: "API 키가 설정되지 않았습니다." }, { status: 500 });
    }

    // 3. Gemini API 초기화 및 호출
    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: "gemini-2.5-flash" }); // 필요에 따라 모델 변경
    
    const result = await model.generateContent(prompt);
    const responseText = result.response.text();

    // 4. 결과를 클라이언트에 반환
    return NextResponse.json({ text: responseText });

  } catch (error) {
    console.error("Gemini API Error:", error);
    return NextResponse.json({ error: "서버 오류가 발생했습니다." }, { status: 500 });
  }
}
