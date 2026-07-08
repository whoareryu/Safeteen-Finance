from dataclasses import dataclass


@dataclass
class MaestroQueryDto:
    question: str


@dataclass
class MaestroResultDto:
    answer: str
    source: str       # "sommelier" | "lens"
    context: list[dict]
