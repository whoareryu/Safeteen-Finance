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
    <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border border-black/[0.08] bg-white p-5">
      <div>
        <label className="text-sm font-medium text-[#1d1d1f]">사이트 주소</label>
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
        <label className="text-sm font-medium text-[#1d1d1f]">명령어</label>
        <input
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          required
          placeholder={
            tab === "crawler"
              ? "몬스테라 키우기 정보를 깊이 2단계까지 찾아줘"
              : "이 페이지에서 몬스테라 관련 내용만 뽑아줘"
          }
          className="mt-1 w-full rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-[#1d1d1f] py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
      >
        {loading ? "처리 중…" : tab === "crawler" ? "크롤링 시작" : "지금 스크랩하기"}
      </button>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {tab === "crawler" && crawlResult && (
        <div className="space-y-1 rounded-xl bg-black/[0.03] p-3 text-sm text-[#1d1d1f]">
          <p>해석된 키워드: {crawlResult.keyword} (depth {crawlResult.depth})</p>
          <p>방문한 페이지: {crawlResult.pages_visited}개</p>
          <p>큐에 쌓인 URL: {crawlResult.urls_queued}개</p>
        </div>
      )}

      {tab === "scraper" && scrapeResult && (
        <div className="space-y-1 rounded-xl bg-black/[0.03] p-3 text-sm text-[#1d1d1f]">
          <p>해석된 키워드: {scrapeResult.keyword}</p>
          <p>{scrapeResult.matched ? `저장됨 → ${scrapeResult.saved_path}` : "스킵 (키워드 불일치)"}</p>
        </div>
      )}
    </form>
  );
}

function CrawlerDoc() {
  return (
    <>
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
          <li>자연어 명령어를 Qwen(1.5B)이 해석해 키워드·탐색 깊이(depth)를 추출</li>
          <li>시드 URL을 큐에 BFS 프론티어로 시작 (depth 0)</li>
          <li>
            <code className="rounded bg-black/[0.04] px-1 py-0.5">plant:visited_urls</code> Set으로 이미 방문한
            URL은 건너뜀 (중복 방지 필터)
          </li>
          <li>방문 처리 후 페이지를 페치하고, 그 URL 자체를 <code className="rounded bg-black/[0.04] px-1 py-0.5">plant:target_urls</code>에 push</li>
          <li>depth가 남아 있으면 페이지에서 같은 도메인 링크만 추출해 다음 depth로 확장</li>
        </ol>
        <p className="text-sm leading-relaxed text-[#3a3a3c]">
          크롤러는 링크 탐색과 중복 제거까지만 책임지고, 키워드 매칭·본문 저장은 스크래퍼 쪽으로
          넘깁니다 (단일 책임 원칙). 위 탭에서 "스크래퍼"를 눌러 이어서 확인하세요.
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
    </>
  );
}

function ScraperDoc() {
  return (
    <>
      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">동작 흐름</h2>
        <ol className="list-decimal space-y-1.5 pl-5 text-sm leading-relaxed text-[#3a3a3c]">
          <li>자연어 명령어를 Qwen(1.5B)이 해석해 키워드를 추출</li>
          <li>입력한 사이트 주소를 동기 HTTP(<code className="rounded bg-black/[0.04] px-1 py-0.5">requests</code>)로 즉시 페치</li>
          <li>BeautifulSoup으로 본문 텍스트 추출 후 키워드 포함 여부 확인</li>
          <li>키워드가 없으면 스킵, 있으면 JSONL 한 줄로 저장 (키워드별 파일에 append)</li>
        </ol>
        <p className="text-sm leading-relaxed text-[#3a3a3c]">
          위 폼은 큐를 거치지 않고 입력한 URL 하나를 즉시 스크랩합니다. 크롤러가 큐에 쌓아둔 URL들을
          순서대로 처리하고 싶다면 아래 CLI를 사용하세요.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">헥사고날 포트</h2>
        <p className="text-sm leading-relaxed text-[#3a3a3c]">
          스크래퍼는 크롤러와 <code className="rounded bg-black/[0.04] px-1 py-0.5">CrawlQueuePort</code>,{" "}
          <code className="rounded bg-black/[0.04] px-1 py-0.5">WebFetcherPort</code>,{" "}
          <code className="rounded bg-black/[0.04] px-1 py-0.5">HtmlParserPort</code>를 공유하고,
          저장 전용으로 <code className="rounded bg-black/[0.04] px-1 py-0.5">ContentStoragePort</code>를 추가로 사용합니다.
          기본 구현체는 로컬 JSONL(<code className="rounded bg-black/[0.04] px-1 py-0.5">JsonlContentStorage</code>)이며,
          포트만 교체하면 S3나 DB 저장으로도 바꿀 수 있습니다.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">CLI 실행 (큐 일괄 처리)</h2>
        <pre className="overflow-x-auto rounded-lg bg-[#1d1d1f] p-4 text-xs leading-relaxed text-[#f5f5f7]">
          <code>{`# 큐에 쌓인 URL을 하나만 처리
python scripts/plant_crawler_cli.py scrape

# 큐가 빌 때까지 반복 처리
python scripts/plant_crawler_cli.py scrape --loop`}</code>
        </pre>
      </section>

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">저장 결과 (JSONL)</h2>
        <pre className="overflow-x-auto rounded-lg bg-[#1d1d1f] p-4 text-xs leading-relaxed text-[#f5f5f7]">
          <code>{`{"url": "https://example-plant-forum.com/monstera-care", "keyword": "몬스테라",
 "title": "몬스테라 키우기 가이드", "text": "몬스테라는 반음지에서 잘 자란다...",
 "extracted_at": "2026-07-16T03:28:06+00:00"}`}</code>
        </pre>
        <p className="text-sm text-[#6e6e73]">
          <code className="rounded bg-black/[0.04] px-1 py-0.5">apps/plant/resources/scraped/{"{키워드}"}.jsonl</code>에
          키워드 단위로 누적 저장되어, <code className="rounded bg-black/[0.04] px-1 py-0.5">training/train_qlora.py</code>의
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
        사이트 주소와 자연어 명령을 입력받아 같은 도메인 내부 링크를 depth 제한까지 탐색하고, 발견한
        URL을 Redis 큐(<code className="rounded bg-black/[0.04] px-1 py-0.5">plant:target_urls</code>)에
        적재하는 Spoke입니다.
      </>
    ),
  },
  {
    id: "scraper",
    label: "스크래퍼",
    title: "스크래퍼 (Content Extractor)",
    description: (
      <>
        사이트 주소와 자연어 명령을 입력받아 그 페이지의 본문을 추출하고, QLoRA 학습용 JSONL
        데이터셋으로 로컬에 적재하는 Spoke입니다.
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
        <div className="mb-4 inline-flex rounded-full border border-black/[0.08] bg-black/[0.02] p-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id)}
              className={cn(
                "rounded-full px-4 py-1.5 text-sm font-medium transition",
                tab === t.id ? "bg-[#1d1d1f] text-white" : "text-[#3a3a3c] hover:text-[#1d1d1f]"
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-[#1d1d1f]">
          {active.title}
        </h1>
        <p className="mt-2 text-sm text-[#6e6e73]">{active.description}</p>
      </header>

      <CrawlScrapeForm tab={tab} />

      {tab === "crawler" ? <CrawlerDoc /> : <ScraperDoc />}
    </div>
  );
}
