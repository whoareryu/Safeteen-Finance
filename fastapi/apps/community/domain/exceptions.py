from __future__ import annotations


class PolicyViolationError(Exception):
    """정책 위반(욕설·혐오 표현)으로 콘텐츠가 차단될 때 발생한다."""

    def __init__(self, score: float, matched: list[str]) -> None:
        self.score = score
        self.matched = matched
        super().__init__(f"정책 위반 차단 (score={score:.2f}, matched={matched})")
