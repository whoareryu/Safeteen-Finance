from __future__ import annotations

import pytest

from safeteen.app.dtos.analysis_dto import AnalysisResult, AnalyzeCommand, RiskLevel
from safeteen.app.ports.output.analysis_model_port import AnalysisModelPort
from safeteen.app.ports.output.policy_matcher_port import PolicyMatcherPort
from safeteen.app.use_cases.analysis_interactor import AnalysisInteractor
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


class _FakeAnalysisModelPort(AnalysisModelPort):
    def __init__(self, result: AnalysisResult) -> None:
        self._result = result
        self.received: tuple[str | None, bytes | None, str | None] | None = None

    async def analyze(
        self, text: str | None, image_bytes: bytes | None, image_content_type: str | None
    ) -> AnalysisResult:
        self.received = (text, image_bytes, image_content_type)
        return self._result


class _FakePolicyMatcher(PolicyMatcherPort):
    def __init__(self, policy: AlternativePolicy | None) -> None:
        self._policy = policy
        self.received: tuple[str, RiskLevel] | None = None

    async def match(self, crime_type: str, risk_level: RiskLevel) -> AlternativePolicy | None:
        self.received = (crime_type, risk_level)
        return self._policy


def _make_result() -> AnalysisResult:
    return AnalysisResult(
        risk_level="DANGER",
        risk_score=92,
        detected_terms=["내구제", "선입금"],
        crime_type="불법 작업대출 및 명의도용",
        legal_warning="대부업법 위반 시 5년 이하 징역 또는 5천만원 이하 벌금에 처해질 수 있습니다.",
        fact_check_summary="선입금을 요구하는 전형적인 불법 작업대출 광고입니다.",
        alternative_policy=None,
    )


async def test_analyze_delegates_to_model_port_and_fills_matched_policy() -> None:
    model_result = _make_result()
    matched_policy = AlternativePolicy(
        title="햇살론 유스", description="사회초년생 대상 저금리 상품", official_link="https://www.kinfa.or.kr"
    )
    model = _FakeAnalysisModelPort(model_result)
    matcher = _FakePolicyMatcher(matched_policy)
    interactor = AnalysisInteractor(model=model, policy_matcher=matcher)

    result = await interactor.analyze(
        AnalyzeCommand(text="내구제 선입금 대출", image_bytes=None, image_content_type=None)
    )

    assert model.received == ("내구제 선입금 대출", None, None)
    assert matcher.received == (model_result.crime_type, model_result.risk_level)
    assert result.alternative_policy is matched_policy
    assert result.risk_level == model_result.risk_level


async def test_analyze_rejects_empty_input() -> None:
    interactor = AnalysisInteractor(model=_FakeAnalysisModelPort(_make_result()), policy_matcher=_FakePolicyMatcher(None))

    with pytest.raises(ValueError):
        await interactor.analyze(AnalyzeCommand(text=None, image_bytes=None, image_content_type=None))
