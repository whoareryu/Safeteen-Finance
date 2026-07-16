"use client";

import { useState } from "react";
import { seedCrawl, type CrawlSeedResult } from "@/lib/crawler-api";

function CrawlerForm() {
  const [seedUrl, setSeedUrl] = useState("");
  const [keyword, setKeyword] = useState("");
  const [depth, setDepth] = useState(2);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CrawlSeedResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await seedCrawl({ seedUrl, keyword, depth }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "크롤링 요청에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border border-black/[0.08] bg-white p-5">
      <div>
        <label className="text-sm font-medium text-[#1d1d1f]">시드 URL</label>
        <input
          value={seedUrl}
          onChange={(e) => setSeedUrl(e.target.value)}
          required
          type="url"
          placeholder="https://example-plant-forum.com"
          className="mt-1 w-full rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
        />
      </div>
      <div>
        <label className="text-sm font-medium text-[#1d1d1f]">키워드</label>
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          required
          placeholder="몬스테라"
          className="mt-1 w-full rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
        />
      </div>
      <div>
        <label className="text-sm font-medium text-[#1d1d1f]">탐색 깊이 (depth)</label>
        <input
          type="number"
          min={0}
          max={5}
          value={depth}
          onChange={(e) => setDepth(Number(e.target.value))}
          className="mt-1 w-full rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-[#1d1d1f] py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
      >
        {loading ? "크롤링 중…" : "크롤링 시작"}
      </button>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {result && (
        <div className="space-y-1 rounded-xl bg-black/[0.03] p-3 text-sm text-[#1d1d1f]">
          <p>방문한 페이지: {result.pages_visited}개</p>
          <p>큐에 쌓인 URL: {result.urls_queued}개 ({result.keyword})</p>
        </div>
      )}
    </form>
  );
}

export default function PlantCrawlerPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-8 px-6 py-10">
      <header className="pt-1">
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-[#1d1d1f]">
          2. 크롤러 (Link Explorer)
        </h1>
        <p className="mt-2 text-sm text-[#6e6e73]">
          시드 URL과 키워드를 입력받아 같은 도메인 내부 링크를 depth 제한까지 탐색하고, 발견한 URL을
          Redis 큐(<code className="rounded bg-black/[0.04] px-1 py-0.5">plant:target_urls</code>)에 적재하는 Spoke입니다.
        </p>
      </header>

      <CrawlerForm />

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">Star Topology — Redis Hub</h2>
        <pre className="overflow-x-auto rounded-lg bg-[#1d1d1f] p-4 text-xs leading-relaxed text-[#f5f5f7]">
          <code>{`                ┌───────────────────────┐
                │       Redis Hub        │
                │ plant:target_urls (큐)  │
                │ plant:visited_urls (셋) │
                └───────────┬───────────┘
                 push        │        pop
        ┌───────────────────┴───────────────────┐
        │                                        │
┌───────▼────────┐                     ┌─────────▼────────┐
│  Crawler        │                     │  Scraper           │
│ (Link Explorer) │                     │ (Content Extractor)│
└─────────────────┘                     └───────────────────┘`}</code>
        </pre>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">동작 흐름</h2>
        <ol className="list-decimal space-y-1.5 pl-5 text-sm leading-relaxed text-[#3a3a3c]">
          <li>시드 URL을 큐에 BFS 프론티어로 시작 (depth 0)</li>
          <li>
            <code className="rounded bg-black/[0.04] px-1 py-0.5">plant:visited_urls</code> Set으로 이미 방문한
            URL은 건너뜀 (중복 방지 필터)
          </li>
          <li>방문 처리 후 페이지를 페치하고, 그 URL 자체를 <code className="rounded bg-black/[0.04] px-1 py-0.5">plant:target_urls</code>에 push</li>
          <li>depth가 남아 있으면 페이지에서 같은 도메인 링크만 추출해 다음 depth로 확장</li>
        </ol>
        <p className="text-sm leading-relaxed text-[#3a3a3c]">
          크롤러는 링크 탐색과 중복 제거까지만 책임지고, 키워드 매칭·본문 저장은{" "}
          <a href="/portfolio/plant/scraper" className="text-[#1d1d1f] underline underline-offset-2">
            스크래퍼
          </a>{" "}
          쪽으로 넘깁니다 (단일 책임 원칙).
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">CLI 실행</h2>
        <pre className="overflow-x-auto rounded-lg bg-[#1d1d1f] p-4 text-xs leading-relaxed text-[#f5f5f7]">
          <code>{`python scripts/plant_crawler_cli.py crawl \\
  --seed-url "https://example-plant-forum.com" \\
  --keyword "몬스테라" \\
  --depth 2`}</code>
        </pre>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">교체 가능한 어댑터</h2>
        <p className="text-sm leading-relaxed text-[#3a3a3c]">
          페처는 <code className="rounded bg-black/[0.04] px-1 py-0.5">WebFetcherPort</code> 뒤에 숨겨져
          있어, 기본 구현체인 <code className="rounded bg-black/[0.04] px-1 py-0.5">requests</code> 기반
          동기 페처를 그대로 두고도 동적 렌더링 페이지가 필요해지면 Selenium/Playwright 어댑터로 교체할 수
          있습니다 — 크롤러·스크래퍼 코드는 변경할 필요가 없습니다 (DIP).
        </p>
      </section>
    </div>
  );
}
