from dataclasses import dataclass, field


@dataclass
class SemanticRoutingQueryDto:
    question: str


@dataclass
class SemanticRoutingResultDto:
    answer: str
    destination: str  # "crud" | "exaone_rag" | "gemini"
    entities: list[str] = field(default_factory=list)
