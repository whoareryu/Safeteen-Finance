from dataclasses import dataclass


@dataclass
class SpamClassificationCommand:
    subject: str
    body: str
    sender: str | None = None


@dataclass
class SpamClassificationResult:
    category: str       # SpamCategory.value
    label: str          # 한글 레이블
    confidence: float   # 0.0–1.0
    is_spam: bool
    reason: str
