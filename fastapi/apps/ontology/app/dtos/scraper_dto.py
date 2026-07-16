from dataclasses import dataclass, field


@dataclass
class ScrapeTargetDto:
    url: str
    keyword: str


@dataclass
class ScrapeResultDto:
    source_url: str
    keyword: str
    matches: list[str] = field(default_factory=list)
    saved_path: str = ""
