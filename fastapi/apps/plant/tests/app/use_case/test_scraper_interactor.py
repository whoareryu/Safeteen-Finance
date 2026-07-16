from __future__ import annotations

from plant.app.use_cases.scraper_interactor import ScraperInteractor
from plant.domain.entities.raw_content_entity import RawContentEntity
from plant.domain.entities.target_url_entity import TargetUrlEntity


class _FakeCrawlQueue:
    def __init__(self, targets: list[TargetUrlEntity]) -> None:
        self._targets = list(targets)

    async def push(self, target):
        raise NotImplementedError

    async def pop(self):
        return self._targets.pop(0) if self._targets else None

    async def is_visited(self, url):
        raise NotImplementedError

    async def mark_visited(self, url):
        raise NotImplementedError


class _FakeWebFetcher:
    def __init__(self, html_by_url: dict[str, str]) -> None:
        self._html_by_url = html_by_url

    def fetch(self, url: str) -> str:
        return self._html_by_url[url]


class _FakeHtmlParser:
    def __init__(self, content: RawContentEntity | None) -> None:
        self._content = content

    def extract_links(self, html, base_url):
        raise NotImplementedError

    def extract_content(self, html, url, keyword):
        return self._content


class _FakeContentStorage:
    def __init__(self) -> None:
        self.saved: list[RawContentEntity] = []

    def save(self, content: RawContentEntity) -> str:
        self.saved.append(content)
        return f"/tmp/{content.keyword}.jsonl"


async def test_scrape_next_saves_matched_content():
    url = "https://forum.example.com/plants/monstera"
    target = TargetUrlEntity(url=url, keyword="몬스테라", depth=1)
    content = RawContentEntity(
        url=url,
        keyword="몬스테라",
        title="몬스테라 키우기",
        text="몬스테라는 반음지에서 잘 자란다.",
        extracted_at="2026-07-16T00:00:00+00:00",
    )

    queue = _FakeCrawlQueue([target])
    storage = _FakeContentStorage()
    interactor = ScraperInteractor(
        queue=queue,
        fetcher=_FakeWebFetcher({url: "<html></html>"}),
        parser=_FakeHtmlParser(content),
        storage=storage,
    )

    result = await interactor.scrape_next()

    assert result.matched is True
    assert result.saved_path == "/tmp/몬스테라.jsonl"
    assert storage.saved == [content]


async def test_scrape_next_returns_none_when_queue_empty():
    interactor = ScraperInteractor(
        queue=_FakeCrawlQueue([]),
        fetcher=_FakeWebFetcher({}),
        parser=_FakeHtmlParser(None),
        storage=_FakeContentStorage(),
    )

    assert await interactor.scrape_next() is None


async def test_scrape_next_skips_when_keyword_not_matched():
    url = "https://forum.example.com/plants/other"
    target = TargetUrlEntity(url=url, keyword="몬스테라", depth=0)
    storage = _FakeContentStorage()

    interactor = ScraperInteractor(
        queue=_FakeCrawlQueue([target]),
        fetcher=_FakeWebFetcher({url: "<html></html>"}),
        parser=_FakeHtmlParser(None),
        storage=storage,
    )

    result = await interactor.scrape_next()

    assert result.matched is False
    assert result.saved_path is None
    assert storage.saved == []
