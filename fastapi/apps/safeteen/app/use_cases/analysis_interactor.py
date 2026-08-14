from __future__ import annotations

from dataclasses import replace

from safeteen.app.dtos.analysis_dto import AnalysisResult, AnalyzeCommand
from safeteen.app.ports.input.analysis_use_case import AnalysisUseCase
from safeteen.app.ports.output.analysis_model_port import AnalysisModelPort
from safeteen.app.ports.output.policy_matcher_port import PolicyMatcherPort


class AnalysisInteractor(AnalysisUseCase):

    def __init__(self, model: AnalysisModelPort, policy_matcher: PolicyMatcherPort) -> None:
        self._model = model
        self._policy_matcher = policy_matcher

    async def analyze(self, command: AnalyzeCommand) -> AnalysisResult:
        if not command.text and not command.image_bytes:
            raise ValueError("text 또는 image 파일 중 하나는 필수입니다.")

        result = await self._model.analyze(command.text, command.image_bytes, command.image_content_type)
        policy = await self._policy_matcher.match(result.crime_type, result.risk_level)
        return replace(result, alternative_policy=policy)
