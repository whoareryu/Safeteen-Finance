from dataclasses import dataclass


@dataclass
class GeminiQueryDto:
    question: str


@dataclass
class GeminiAnswerDto:
    answer: str
