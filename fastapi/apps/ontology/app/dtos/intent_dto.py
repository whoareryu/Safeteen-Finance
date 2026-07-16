from dataclasses import dataclass, field


@dataclass
class IntentDto:
    destination: str  # "crud" | "qwen_rag" | "gemini"
    entities: list[str] = field(default_factory=list)
