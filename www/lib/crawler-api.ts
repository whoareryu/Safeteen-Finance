export interface CrawlSeedResult {
  seed_url: string;
  keyword: string;
  depth: number;
  pages_visited: number;
  urls_queued: number;
  saved_path?: string;
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

export async function seedCrawl(params: { seedUrl: string; command: string }): Promise<CrawlSeedResult> {
  const res = await fetch("/api/plant/crawler/seed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seed_url: params.seedUrl, command: params.command }),
  });
  return parseOrThrow<CrawlSeedResult>(res);
}

export async function scrapeUrl(params: { seedUrl: string; command: string }): Promise<ScrapeRunResult> {
  const res = await fetch("/api/plant/scraper/run-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seed_url: params.seedUrl, command: params.command }),
  });
  return parseOrThrow<ScrapeRunResult>(res);
}
