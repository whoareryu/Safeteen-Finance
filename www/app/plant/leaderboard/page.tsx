"use client";

import { useEffect, useState } from "react";
import { getLeaderboard, type LeaderboardEntry } from "@/lib/my-plants-api";

const STAGE_EMOJI: Record<string, string> = {
  새싹: "🌱",
  새순: "🌿",
  성목: "🌳",
};

const RANK_MEDAL: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

export default function LeaderboardPage() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLeaderboard(50)
      .then(setEntries)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-semibold text-foreground">식물집사 랭킹</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        포인트가 높은 순서로 식물집사들을 보여줘요.
      </p>

      {loading ? (
        <p className="mt-6 text-sm text-muted-foreground">불러오는 중…</p>
      ) : entries.length === 0 ? (
        <p className="mt-6 text-sm text-muted-foreground">아직 랭킹에 등록된 식물이 없어요.</p>
      ) : (
        <div className="mt-6 space-y-2">
          {entries.map((e) => (
            <div
              key={e.plant_id}
              className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 shadow-sm"
            >
              <span className="w-8 shrink-0 text-center text-lg font-semibold text-foreground">
                {RANK_MEDAL[e.rank] ?? e.rank}
              </span>
              <span className="text-xl" aria-hidden>
                {STAGE_EMOJI[e.growth_stage] ?? "🌱"}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium text-foreground">{e.nickname}</p>
                <p className="text-xs text-muted-foreground">{e.species_name}</p>
              </div>
              <span className="shrink-0 font-semibold text-primary">{e.points}P</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
