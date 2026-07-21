from dataclasses import dataclass


@dataclass(frozen=True)
class SentimentAnalyzeCommand:

    text: str


@dataclass(frozen=True)
class SentimentScore:

    label: str
    score: float


@dataclass(frozen=True)
class SentimentAnalyzeResult:

    sentiment: str
    confidence: float
    scores: list[SentimentScore]
