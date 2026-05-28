from fastapi import HTTPException

from apps.matrix.app.keymaker import MissingGeminiKeyError, keymaker
from apps.titanic.app.use_cases.titanic_schemas import ChatMessage


def gemini_error_detail(exc: Exception) -> tuple[int, str]:
    msg = str(exc)
    upper = msg.upper()
    if "API_KEY_INVALID" in upper or "API KEY NOT FOUND" in upper:
        return (
            503,
            "GEMINI_API_KEY가 유효하지 않습니다. backend/.env 에 Google AI Studio에서 발급한 키를 넣고 서버를 재시작하세요.",
        )
    if "PERMISSION_DENIED" in upper or "403" in msg:
        return 503, "Gemini API 권한이 없습니다. API 키와 프로젝트 설정을 확인하세요."
    if "QUOTA" in upper or "RESOURCE_EXHAUSTED" in upper:
        return 503, "Gemini API 할당량이 초과되었습니다. 잠시 후 다시 시도하세요."
    return 502, msg


def messages_to_gemini_contents(messages: list[ChatMessage]) -> list[dict]:
    out: list[dict] = []
    for m in messages:
        role = "model" if m.role == "assistant" else "user"
        text = m.content.strip()
        if not text:
            raise HTTPException(status_code=422, detail="빈 content는 허용되지 않습니다.")
        out.append({"role": role, "parts": [text]})
    return out


def generate_chat_text(messages: list[ChatMessage], model: str | None) -> tuple[str, str]:
    if messages[-1].role != "user":
        raise HTTPException(
            status_code=422,
            detail="messages의 마지막 요소는 role=user 여야 합니다.",
        )
    try:
        gemini = keymaker.generative_model(model)
        model_used = keymaker.resolve_model_name(model or keymaker.gemini_model_name)
    except MissingGeminiKeyError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    contents = messages_to_gemini_contents(messages)
    try:
        response = gemini.generate_content(contents)
    except Exception as e:
        status, detail = gemini_error_detail(e)
        raise HTTPException(status_code=status, detail=detail) from e

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise HTTPException(
            status_code=502,
            detail="모델이 텍스트 응답을 반환하지 않았습니다.",
        )
    return text, model_used
