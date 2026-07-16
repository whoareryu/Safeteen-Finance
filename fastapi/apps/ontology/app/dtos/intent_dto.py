from dataclasses import dataclass, field


@dataclass
class IntentDto:
    destination: str  # "crud" | "exaone_rag" | "gemini"
    entities: list[str] = field(default_factory=list)
