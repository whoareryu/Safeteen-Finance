from dataclasses import dataclass, field


@dataclass
class CrawlTargetDto:
    url: str
    keyword: str


@dataclass
class CrawledPageDto:
    url: str
    title: str
    text: str
    links: list[str]


@dataclass
class CrawlResultDto:
    source_url: str
    keyword: str
    pages: list[CrawledPageDto] = field(default_factory=list)
    saved_path: str = ""
