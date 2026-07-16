"""식물 지식 크롤러/스크래퍼 CLI — Redis Hub(plant:target_urls) 기반 Star Topology.

사용 (backend 루트에서):
  python scripts/plant_crawler_cli.py crawl --seed-url "https://example-plant-forum.com" --keyword "몬스테라" --depth 2
  python scripts/plant_crawler_cli.py scrape
  python scripts/plant_crawler_cli.py scrape --loop   # 큐가 빌 때까지 반복
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))
if str(_backend_root / "apps") not in sys.path:
    sys.path.insert(0, str(_backend_root / "apps"))

from dotenv import load_dotenv

load_dotenv(_backend_root / ".env")

from plant.app.dtos.crawler_dto import CrawlCommand
from plant.dependencies.crawler_provider import get_crawler_use_case
from plant.dependencies.scraper_provider import get_scraper_use_case


async def _run_crawl(args: argparse.Namespace) -> None:
    use_case = get_crawler_use_case()
    result = await use_case.crawl(
        CrawlCommand(seed_url=args.seed_url, keyword=args.keyword, depth=args.depth)
    )
    print(
        f"crawl 완료: seed={result.seed_url} keyword={result.keyword} "
        f"pages_visited={result.pages_visited} urls_queued={result.urls_queued}"
    )


async def _run_scrape(args: argparse.Namespace) -> None:
    use_case = get_scraper_use_case()
    processed = 0
    while True:
        result = await use_case.scrape_next()
        if result is None:
            break
        processed += 1
        status = f"saved -> {result.saved_path}" if result.matched else "skipped (키워드 불일치)"
        print(f"[{processed}] {result.url}: {status}")
        if not args.loop:
            break

    if processed == 0:
        print("큐가 비어 있습니다 (plant:target_urls).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plant Crawler/Scraper CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    crawl_parser = subparsers.add_parser("crawl", help="사이트를 탐색해 대상 URL을 Redis 큐에 적재한다")
    crawl_parser.add_argument("--seed-url", required=True)
    crawl_parser.add_argument("--keyword", required=True)
    crawl_parser.add_argument("--depth", type=int, default=2)
    crawl_parser.set_defaults(func=_run_crawl)

    scrape_parser = subparsers.add_parser("scrape", help="큐에서 URL을 꺼내 본문을 추출하고 JSONL로 저장한다")
    scrape_parser.add_argument("--loop", action="store_true", help="큐가 빌 때까지 반복 처리")
    scrape_parser.set_defaults(func=_run_scrape)

    args = parser.parse_args()
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
