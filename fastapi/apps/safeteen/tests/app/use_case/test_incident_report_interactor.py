from __future__ import annotations

import pytest

from safeteen.app.dtos.incident_report_dto import IncidentReportCommand, IncidentReportResult
from safeteen.app.ports.output.incident_report_generator_port import IncidentReportGeneratorPort
from safeteen.app.use_cases.incident_report_interactor import IncidentReportInteractor


class _FakeIncidentReportGenerator(IncidentReportGeneratorPort):
    def __init__(self, result: IncidentReportResult) -> None:
        self._result = result
        self.received: tuple[str, bytes | None, str | None] | None = None

    async def generate(
        self, situation: str, image_bytes: bytes | None, image_content_type: str | None
    ) -> IncidentReportResult:
        self.received = (situation, image_bytes, image_content_type)
        return self._result


def _make_result() -> IncidentReportResult:
    return IncidentReportResult(
        incident_summary="2026년 8월, 텔레그램에서 작업대출을 빙자한 사기를 당함.",
        victim_statement="상대방이 선입금을 요구하여 30만원을 송금하였으나 이후 연락이 두절됨.",
        evidence_list=["대화 캡처 화면", "송금 내역", "상대방 계좌번호"],
        requested_action="계좌 지급정지 협조 및 수사 개시를 요청함.",
    )


async def test_generate_delegates_to_generator_port() -> None:
    expected = _make_result()
    generator = _FakeIncidentReportGenerator(expected)
    interactor = IncidentReportInteractor(generator=generator)

    result = await interactor.generate(
        IncidentReportCommand(situation="선입금 요구 후 연락 두절됐어요", image_bytes=None, image_content_type=None)
    )

    assert generator.received == ("선입금 요구 후 연락 두절됐어요", None, None)
    assert result is expected


async def test_generate_rejects_blank_situation() -> None:
    interactor = IncidentReportInteractor(generator=_FakeIncidentReportGenerator(_make_result()))

    with pytest.raises(ValueError):
        await interactor.generate(IncidentReportCommand(situation="   ", image_bytes=None, image_content_type=None))
