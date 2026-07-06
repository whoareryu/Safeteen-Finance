"use client";

import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/components/auth-provider";

interface TelegramHistoryItem {
  text: string;
  sent_at: string;
}

async function fetchHistory(): Promise<TelegramHistoryItem[]> {
  const res = await fetch("/api/chef/telegram/history");
  if (!res.ok) throw new Error(`불러오기 실패 (${res.status})`);
  return res.json();
}

export default function TelegramPage() {
  const { isOwner } = useAuth();
  const [messages, setMessages] = useState<TelegramHistoryItem[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOwner) {
      setLoading(false);
      return;
    }
    setLoading(true);
    fetchHistory()
      .then(setMessages)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [isOwner]);

  const filtered = messages.filter((m) =>
    m.text.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <main className="mx-auto max-w-lg px-4 pb-28 pt-6">
      <h1 className="mb-5 text-xl font-bold">텔레그램 알림 로그</h1>

      {!isOwner ? (
        <div className="rounded-lg border border-border bg-muted/40 px-4 py-6 text-center text-sm text-muted-foreground">
          본인 계정으로 로그인해야 이용할 수 있습니다.
        </div>
      ) : (
        <>
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="메시지 검색"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className={cn(
                "w-full rounded-lg border bg-background py-2.5 pl-9 pr-4 text-sm outline-none",
                "placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/40"
              )}
            />
          </div>

          {loading && (
            <p className="text-sm text-muted-foreground">불러오는 중...</p>
          )}

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          {!loading && !error && filtered.length === 0 && (
            <p className="text-sm text-muted-foreground">
              {query ? "검색 결과가 없습니다" : "전송된 메시지가 없습니다"}
            </p>
          )}

          {!loading && !error && filtered.length > 0 && (
            <ul className="space-y-3">
              {filtered.map((msg, i) => (
                <li key={i} className="rounded-lg border bg-card p-4">
                  <pre className="whitespace-pre-wrap font-sans text-sm text-foreground">
                    {msg.text}
                  </pre>
                  <p className="mt-2 text-xs text-muted-foreground">
                    {new Date(msg.sent_at).toLocaleString("ko-KR")}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </main>
  );
}
