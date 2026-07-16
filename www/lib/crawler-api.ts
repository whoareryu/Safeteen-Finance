export interface CrawlSeedResult {
  seed_url: string;
  keyword: string;
  pages_visited: number;
  urls_queued: number;
}

export interface ScrapeRunResult {
  ran: boolean;
  url?: string;
  keyword?: string;
  matched?: boolean;
  saved_path?: string;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  const data = (await res.json().catch(() => ({}))) as T & { detail?: unknown };
  if (!res.ok) {
    const detail = typeof data?.detail === "string" ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

export async function seedCrawl(params: {
  seedUrl: string;
  keyword: string;
  depth: number;
}): Promise<CrawlSeedResult> {
  const res = await fetch("/api/plant/crawler/seed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seed_url: params.seedUrl, keyword: params.keyword, depth: params.depth }),
  });
  return parseOrThrow<CrawlSeedResult>(res);
}

export async function runScrapeOnce(): Promise<ScrapeRunResult> {
  const res = await fetch("/api/plant/scraper/run", { method: "POST" });
  return parseOrThrow<ScrapeRunResult>(res);
}
