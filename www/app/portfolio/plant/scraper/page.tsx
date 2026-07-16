"use client";

import { useState } from "react";
import { runScrapeOnce, type ScrapeRunResult } from "@/lib/crawler-api";

function ScraperRunner() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<ScrapeRunResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const onRun = async () => {
    setRunning(true);
    setError(null);
    setResults([]);
    try {
      // 큐가 빌 때까지 하나씩 처리 (CLI의 `scrape --loop`와 동일한 동작)
      for (;;) {
        const result = await runScrapeOnce();
        if (!result.ran) break;
        setResults((prev) => [...prev, result]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "스크래핑 요청에 실패했습니다.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-3 rounded-2xl border border-black/[0.08] bg-white p-5">
      <p className="text-sm text-[#3a3a3c]">
        크롤러가 큐에 쌓아둔 URL을 하나씩 꺼내 본문을 추출하고, 키워드가 포함된 페이지만 JSONL로 저장합니다.
      </p>
      <button
        type="button"
        onClick={() => void onRun()}
        disabled={running}
        className="w-full rounded-lg bg-[#1d1d1f] py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
      >
        {running ? "큐 처리 중…" : "지금 큐 처리하기"}
      </button>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {results.length > 0 && (
        <ul className="space-y-1.5 text-sm text-[#1d1d1f]">
          {results.map((r, i) => (
            <li key={i} className="rounded-lg bg-black/[0.03] px-3 py-2">
              {r.matched ? `저장됨 → ${r.saved_path}` : "스킵 (키워드 불일치)"} · {r.url}
            </li>
          ))}
        </ul>
      )}
      {!running && results.length === 0 && (
        <p className="text-sm text-[#6e6e73]">아직 실행 전이거나 큐가 비어 있습니다.</p>
      )}
    </div>
  );
}

export default function PlantScraperPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-8 px-6 py-10">
      <header className="pt-1">
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-[#1d1d1f]">
          1. 스크래퍼 (Content Extractor)
        </h1>
        <p className="mt-2 text-sm text-[#6e6e73]">
          Redis 큐(<code className="rounded bg-black/[0.04] px-1 py-0.5">plant:target_urls</code>)에서
          대상 URL을 하나씩 꺼내 본문을 추출하고, QLoRA 학습용 JSONL 데이터셋으로 로컬에 적재하는 Spoke입니다.
        </p>
      </header>

      <ScraperRunner />

      <section className="space-y-3">
        <h2 className="text-base font-semibold text-[#1d1d1f]">동작 흐름</h2>
        <ol className="list-decimal space-y-1.5 pl-5 text-sm leading-relaxed text-[#3a3a3c]">
          <li>큐에서 <code className="rounded bg-black/[0.04] px-1 py-0.5">TargetUrlEntity</code> 하나를 POP</li>
          <li>해당 URL을 동기 HTTP(<code className="rounded bg-black/[0.04] px-1 py-0.5">requests</code>)로 페치</li>
          <li>BeautifulSoup으로 본문 텍스트 추출 후 키워드 포함 여부 확인</li>
          <li>키워드가 없으면 스킵, 있으면 JSONL 한 줄로 저장 (키워드별 파일에 append)</li>
        </ol>
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
        <h2 className="text-base font-semibold text-[#1d1d1f]">CLI 실행</h2>
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

      <p className="text-sm text-[#6e6e73]">
        큐를 채우는 단계는{" "}
        <a href="/portfolio/plant/crawler" className="text-[#1d1d1f] underline underline-offset-2">
          2. 크롤러
        </a>
        에서 이어집니다.
      </p>
    </div>
  );
}
