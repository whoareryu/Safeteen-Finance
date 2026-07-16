"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { seedCrawl, scrapeUrl, type CrawlSeedResult, type ScrapeRunResult } from "@/lib/crawler-api";

type Tab = "crawler" | "scraper";

function CrawlScrapeForm({ tab }: { tab: Tab }) {
  const [seedUrl, setSeedUrl] = useState("");
  const [command, setCommand] = useState("");
  const [loading, setLoading] = useState(false);
  const [crawlResult, setCrawlResult] = useState<CrawlSeedResult | null>(null);
  const [scrapeResult, setScrapeResult] = useState<ScrapeRunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setCrawlResult(null);
    setScrapeResult(null);
    try {
      if (tab === "crawler") {
        setCrawlResult(await seedCrawl({ seedUrl, command }));
      } else {
        setScrapeResult(await scrapeUrl({ seedUrl, command }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "요청에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border border-border bg-card p-5">
      <div>
        <label className="text-sm font-medium text-foreground">URL</label>
        <input
          value={seedUrl}
          onChange={(e) => setSeedUrl(e.target.value)}
          required
          type="url"
          placeholder="https://example-plant-forum.com"
          className="mt-1 w-full rounded-lg border border-border bg-input px-3 py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-ring/30"
        />
      </div>
      <div>
        <label className="text-sm font-medium text-foreground">키워드</label>
        <input
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          required
          placeholder={
            tab === "crawler"
              ? "몬스테라 키우기 정보를 깊이 2단계까지 찾아줘"
              : "이 페이지에서 몬스테라 관련 내용만 뽑아줘"
          }
          className="mt-1 w-full rounded-lg border border-border bg-input px-3 py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-ring/30"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-primary py-2.5 text-sm font-semibold text-primary-foreground transition disabled:opacity-50"
      >
        {loading ? "처리 중…" : tab === "crawler" ? "크롤링 시작" : "지금 스크랩하기"}
      </button>

      {error && <p className="text-sm text-destructive">{error}</p>}

      {tab === "crawler" && crawlResult && (
        <div className="space-y-1 rounded-xl bg-muted/50 p-3 text-sm text-foreground">
          <p>해석된 키워드: {crawlResult.keyword} (depth {crawlResult.depth})</p>
          <p>방문한 페이지: {crawlResult.pages_visited}개</p>
          <p>큐에 쌓인 URL: {crawlResult.urls_queued}개</p>
          {crawlResult.saved_path && <p>저장 위치: {crawlResult.saved_path}</p>}
        </div>
      )}

      {tab === "scraper" && scrapeResult && (
        <div className="space-y-1 rounded-xl bg-muted/50 p-3 text-sm text-foreground">
          <p>해석된 키워드: {scrapeResult.keyword}</p>
          <p>{scrapeResult.matched ? "키워드 포함된 문단을 찾았습니다" : "키워드를 포함한 문단을 찾지 못했습니다"}</p>
          {scrapeResult.saved_path && <p>저장 위치: {scrapeResult.saved_path}</p>}
        </div>
      )}
    </form>
  );
}

function CrawlerDoc() {
  return (
    <>
      <section className="space-y-3">
        <h2 className="text-base font-semibold text-foreground">Star Topology — Redis Hub</h2>
        <pre className="overflow-x-auto rounded-lg bg-[#1d1d1f] p-4 text-xs leading-relaxed text-[#f5f5f7]">
          <code>{`                ┌───────────────────────┐
                │       Redis Hub        │
                │ ontology:crawler:queue │
                │ ontology:scraper:queue │
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
        <h2 className="text-base font-semibold text-foreground">동작 흐름</h2>
        <ol className="list-decimal space-y-1.5 pl-5 text-sm leading-relaxed text-muted-foreground">
          <li>키워드를 Qwen(1.5B)이 해석해 검색 키워드·탐색 깊이(depth)를 추출</li>
          <li>URL과 키워드를 ontology 허브의 Redis 큐(<code className="rounded bg-muted px-1 py-0.5">ontology:crawler:queue</code>)에 적재</li>
          <li>큐에서 즉시 꺼내 BFS로 같은 도메인 링크를 depth 제한까지 탐색</li>
          <li>방문한 페이지의 제목·본문·링크를 모아 <code className="rounded bg-muted px-1 py-0.5">ontology/resources/crawled/</code>에 JSONL로 저장</li>
        </ol>
        <p className="text-sm leading-relaxed text-muted-foreground">
          크롤러는 링크 탐색과 본문 수집까지 책임지고, 키워드 매칭이 필요한 스크래핑은 위 탭에서
          "스크래퍼"를 눌러 이어서 확인하세요.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-foreground">CLI 실행</h2>
        <pre className="overflow-x-auto rounded-lg bg-[#1d1d1f] p-4 text-xs leading-relaxed text-[#f5f5f7]">
          <code>{`python scripts/plant_crawler_cli.py crawl \\
  --seed-url "https://example-plant-forum.com" \\
  --keyword "몬스테라" \\
  --depth 2`}</code>
        </pre>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-foreground">교체 가능한 어댑터</h2>
        <p className="text-sm leading-relaxed text-muted-foreground">
          페처는 <code className="rounded bg-muted px-1 py-0.5">WebFetcherPort</code> 뒤에 숨겨져
          있어, 기본 구현체인 <code className="rounded bg-muted px-1 py-0.5">httpx</code> 기반
          동기 페처를 그대로 두고도 동적 렌더링 페이지가 필요해지면 Selenium/Playwright 어댑터로 교체할 수
          있습니다 — 크롤러·스크래퍼 코드는 변경할 필요가 없습니다 (DIP).
        </p>
      </section>
    </>
  );
}

function ScraperDoc() {
  return (
    <>
      <section className="space-y-3">
        <h2 className="text-base font-semibold text-foreground">동작 흐름</h2>
        <ol className="list-decimal space-y-1.5 pl-5 text-sm leading-relaxed text-muted-foreground">
          <li>키워드를 Qwen(1.5B)이 해석해 검색 키워드를 추출</li>
          <li>URL과 키워드를 ontology 허브의 Redis 큐(<code className="rounded bg-muted px-1 py-0.5">ontology:scraper:queue</code>)에 적재</li>
          <li>큐에서 즉시 꺼내 페이지를 페치하고 BeautifulSoup으로 본문 태그(p/li/h1~h3)에서 키워드 포함 문단만 추출</li>
          <li>결과를(문단이 없어도) <code className="rounded bg-muted px-1 py-0.5">ontology/resources/scraped/</code>에 JSONL로 저장</li>
        </ol>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-foreground">헥사고날 포트</h2>
        <p className="text-sm leading-relaxed text-muted-foreground">
          스크래퍼는 크롤러와 <code className="rounded bg-muted px-1 py-0.5">WebFetcherPort</code>를 공유하고,
          큐는 <code className="rounded bg-muted px-1 py-0.5">ScrapeTargetQueuePort</code>, 저장은{" "}
          <code className="rounded bg-muted px-1 py-0.5">ScrapeResultSinkPort</code>로 분리되어 있습니다.
          기본 구현체는 로컬 JSONL(<code className="rounded bg-muted px-1 py-0.5">JsonlScrapeResultSink</code>)이며,
          포트만 교체하면 S3나 DB 저장으로도 바꿀 수 있습니다.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-foreground">저장 결과 (JSONL)</h2>
        <pre className="overflow-x-auto rounded-lg bg-[#1d1d1f] p-4 text-xs leading-relaxed text-[#f5f5f7]">
          <code>{`{"url": "https://example-plant-forum.com/monstera-care", "keyword": "몬스테라",
 "match": "몬스테라는 반음지에서 잘 자란다...",
 "scraped_at": "20260716T032806Z"}`}</code>
        </pre>
        <p className="text-sm text-muted-foreground">
          <code className="rounded bg-muted px-1 py-0.5">ontology/resources/scraped/{"{도메인}_{시각}"}.jsonl</code>에
          호출 단위로 저장되어, <code className="rounded bg-muted px-1 py-0.5">training/train_qlora.py</code>의
          입력 데이터셋으로 바로 이어집니다.
        </p>
      </section>
    </>
  );
}

const TABS: { id: Tab; label: string; title: string; description: React.ReactNode }[] = [
  {
    id: "crawler",
    label: "크롤러",
    title: "크롤러 (Link Explorer)",
    description: (
      <>
        URL과 키워드를 입력받아 같은 도메인 내부 링크를 depth 제한까지 탐색하고, 방문한 페이지를
        Redis 큐(<code className="rounded bg-muted px-1 py-0.5">ontology:crawler:queue</code>)를 거쳐
        JSONL로 저장하는 Spoke입니다.
      </>
    ),
  },
  {
    id: "scraper",
    label: "스크래퍼",
    title: "스크래퍼 (Content Extractor)",
    description: (
      <>
        URL과 키워드를 입력받아 그 페이지에서 키워드가 포함된 문단을 추출하고, JSONL 데이터셋으로
        저장하는 Spoke입니다.
      </>
    ),
  },
];

export default function PlantCrawlerScraperPage() {
  const [tab, setTab] = useState<Tab>("crawler");
  const active = TABS.find((t) => t.id === tab)!;

  return (
    <div className="mx-auto max-w-2xl space-y-8 px-6 py-10">
      <header className="pt-1">
        <div className="mb-4 inline-flex rounded-full border border-border bg-muted/40 p-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id)}
              className={cn(
                "rounded-full px-4 py-1.5 text-sm font-medium transition",
                tab === t.id
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-foreground">
          {active.title}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">{active.description}</p>
      </header>

      <CrawlScrapeForm tab={tab} />

      {tab === "crawler" ? <CrawlerDoc /> : <ScraperDoc />}
    </div>
  );
}
