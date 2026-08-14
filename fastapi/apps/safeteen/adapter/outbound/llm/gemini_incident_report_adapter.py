from __future__ import annotations

from google import genai
from google.genai import types
from pydantic import BaseModel

from core.infra.secret_manager import secret_manager

from safeteen.app.dtos.incident_report_dto import IncidentReportResult
from safeteen.app.ports.output.incident_report_generator_port import IncidentReportGeneratorPort

_MODEL = "gemini-flash-latest"

_PROMPT = (
    "너는 금융 사기 피해자가 경찰서에 제출할 '피해 경위서 및 증거 제출 서식'을 작성해 주는 "
    "법률 문서 작성 보조원이야. 아래는 피해자가 직접 입력한 피해 정황(및 증거 캡처 이미지)이야. "
    "이를 바탕으로 다음을 작성해줘.\n"
    "1. incident_summary: 사건 개요를 한국어로 육하원칙에 맞게 정리한 한 문단.\n"
    "2. victim_statement: 경찰 제출용 피해자 진술서 문체(공손하고 사실 위주)로 작성한 상세 진술.\n"
    "3. evidence_list: 함께 제출하면 좋은 증거 자료 목록 (예: '대화 캡처 화면', '송금 내역', "
    "'상대방 계좌번호'). 피해자가 이미 언급/첨부한 것과 앞으로 확보해야 할 것을 모두 포함.\n"
    "4. requested_action: 경찰에게 요청할 조치(예: 계좌 지급정지 협조 요청, 수사 개시 요청)를 "
    "요약한 문장."
)


class _IncidentReportSchema(BaseModel):
    incident_summary: str
    victim_statement: str
    evidence_list: list[str]
    requested_action: str


class GeminiIncidentReportAdapter(IncidentReportGeneratorPort):
    """Outbound 어댑터 — Gemini Structured Output으로 피해 경위서 초안을 생성한다."""

    def __init__(self, api_key: str | None = None, model: str = _MODEL) -> None:
        resolved_key = api_key or secret_manager.get_secret("GEMINI_API_KEY")
        self._client = genai.Client(api_key=resolved_key)
        self._model = model

    async def generate(
        self, situation: str, image_bytes: bytes | None, image_content_type: str | None
    ) -> IncidentReportResult:
        contents: list[types.Part | str] = [_PROMPT, situation]
        if image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_content_type or "image/jpeg"))

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_IncidentReportSchema,
            ),
        )
        parsed = response.parsed
        if not isinstance(parsed, _IncidentReportSchema):
            raise ValueError("Gemini가 피해 경위서를 구조화된 형식으로 반환하지 않았습니다.")

        return IncidentReportResult(
            incident_summary=parsed.incident_summary,
            victim_statement=parsed.victim_statement,
            evidence_list=parsed.evidence_list,
            requested_action=parsed.requested_action,
        )
