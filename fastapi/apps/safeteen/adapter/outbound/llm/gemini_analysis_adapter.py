from __future__ import annotations

from typing import Literal

from google import genai
from google.genai import types
from pydantic import BaseModel

from core.infra.secret_manager import secret_manager

from safeteen.app.dtos.analysis_dto import AnalysisResult
from safeteen.app.ports.output.analysis_model_port import AnalysisModelPort

_MODEL = "gemini-flash-latest"

_PROMPT = (
    "너는 청소년·청년 대상 SNS(인스타그램, 텔레그램 등) 불법 금융 광고를 탐지하는 "
    "금융감독원 수준의 팩트체크 전문가야. 아래 텍스트/이미지는 SNS에서 캡처한 대출·구인 "
    "광고일 수 있어. 다음을 분석해줘.\n"
    "1. risk_level: 불법 작업대출, 대포통장, 내구제 대출, 명의도용 등의 정황이 전혀 없으면 "
    "SAFE, 의심 정황이 있으면 WARNING, 명백한 불법 금융/사기 정황이면 DANGER.\n"
    "2. risk_score: 0(안전)~100(매우 위험) 사이의 위험도 점수.\n"
    "3. detected_terms: '내구제', '선입금', '고금리 작업대출' 등 감지된 불법 은어 목록. "
    "없으면 빈 배열.\n"
    "4. crime_type: 의심되는 범죄 유형을 한국어로 (예: '불법 작업대출 및 명의도용'). "
    "혐의가 없으면 '해당 없음'.\n"
    "5. legal_warning: 관련 법률과 처벌 수위를 요약한 경고문.\n"
    "6. fact_check_summary: 이 게시물이 왜 위험한지(또는 왜 안전한지) 요약한 설명."
)


class _AnalysisResultSchema(BaseModel):
    risk_level: Literal["SAFE", "WARNING", "DANGER"]
    risk_score: int
    detected_terms: list[str]
    crime_type: str
    legal_warning: str
    fact_check_summary: str


class GeminiAnalysisAdapter(AnalysisModelPort):
    """Outbound 어댑터 — Gemini 멀티모달 Structured Output으로 SNS 광고 위험도를 분석한다.

    대안 정책(alternative_policy)은 Gemini가 지어내면 URL·수치가 부정확할 위험이 있어
    여기서는 채우지 않는다 — 규칙 기반 PolicyMatcherPort가 별도로 매칭한다.
    """

    def __init__(self, api_key: str | None = None, model: str = _MODEL) -> None:
        resolved_key = api_key or secret_manager.get_secret("GEMINI_API_KEY")
        self._client = genai.Client(api_key=resolved_key)
        self._model = model

    async def analyze(
        self, text: str | None, image_bytes: bytes | None, image_content_type: str | None
    ) -> AnalysisResult:
        contents: list[types.Part | str] = [_PROMPT]
        if text:
            contents.append(text)
        if image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_content_type or "image/jpeg"))

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_AnalysisResultSchema,
            ),
        )
        parsed = response.parsed
        if not isinstance(parsed, _AnalysisResultSchema):
            raise ValueError("Gemini가 분석 결과를 구조화된 형식으로 반환하지 않았습니다.")

        return AnalysisResult(
            risk_level=parsed.risk_level,
            risk_score=parsed.risk_score,
            detected_terms=parsed.detected_terms,
            crime_type=parsed.crime_type,
            legal_warning=parsed.legal_warning,
            fact_check_summary=parsed.fact_check_summary,
            alternative_policy=None,
        )
