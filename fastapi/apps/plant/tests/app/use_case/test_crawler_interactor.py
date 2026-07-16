from __future__ import annotations

from plant.app.dtos.crawler_dto import CrawlCommand
from plant.app.use_cases.crawler_interactor import CrawlerInteractor
from plant.domain.entities.target_url_entity import TargetUrlEntity


class _FakeCrawlQueue:
    def __init__(self) -> None:
        self.visited: set[str] = set()
        self.pushed: list[TargetUrlEntity] = []

    async def push(self, target: TargetUrlEntity) -> None:
        self.pushed.append(target)

    async def pop(self):
        raise NotImplementedError

    async def is_visited(self, url: str) -> bool:
        return url in self.visited

    async def mark_visited(self, url: str) -> None:
        self.visited.add(url)


class _FakeWebFetcher:
    def __init__(self, pages: dict[str, str]) -> None:
        self._pages = pages

    def fetch(self, url: str) -> str:
        return self._pages[url]


class _FakeHtmlParser:
    def __init__(self, links_by_url: dict[str, list[str]]) -> None:
        self._links_by_url = links_by_url

    def extract_links(self, html: str, base_url: str) -> list[str]:
        return self._links_by_url.get(base_url, [])

    def extract_content(self, html, url, keyword):
        raise NotImplementedError


async def test_crawl_discovers_same_domain_links_within_depth():
    seed = "https://forum.example.com/plants"
    child = "https://forum.example.com/plants/monstera"
    outside = "https://other.example.com/spam"

    queue = _FakeCrawlQueue()
    fetcher = _FakeWebFetcher({seed: "<html>seed</html>", child: "<html>child</html>"})
    parser = _FakeHtmlParser({seed: [child, outside]})

    interactor = CrawlerInteractor(queue=queue, fetcher=fetcher, parser=parser)
    result = await interactor.crawl(CrawlCommand(seed_url=seed, keyword="몬스테라", depth=1))

    queued_urls = {t.url for t in queue.pushed}
    assert queued_urls == {seed, child}
    assert outside not in queued_urls
    assert result.pages_visited == 2
    assert result.urls_queued == 2


async def test_crawl_skips_already_visited_seed():
    seed = "https://forum.example.com/plants"
    queue = _FakeCrawlQueue()
    queue.visited.add(seed)

    interactor = CrawlerInteractor(
        queue=queue, fetcher=_FakeWebFetcher({}), parser=_FakeHtmlParser({})
    )
    result = await interactor.crawl(CrawlCommand(seed_url=seed, keyword="몬스테라", depth=1))

    assert result.pages_visited == 0
    assert result.urls_queued == 0


async def test_crawl_does_not_expand_links_at_max_depth():
    seed = "https://forum.example.com/plants"
    child = "https://forum.example.com/plants/monstera"

    queue = _FakeCrawlQueue()
    fetcher = _FakeWebFetcher({seed: "<html>seed</html>"})
    parser = _FakeHtmlParser({seed: [child]})

    interactor = CrawlerInteractor(queue=queue, fetcher=fetcher, parser=parser)
    result = await interactor.crawl(CrawlCommand(seed_url=seed, keyword="몬스테라", depth=0))

    assert {t.url for t in queue.pushed} == {seed}
    assert result.pages_visited == 1
