"use client";

import { useState } from "react";
import { fetchCourse, type CourseStop } from "@/lib/gourmet-tabs";

export default function CoupleTravelPage() {
  const [district, setDistrict] = useState("");
  const [stops, setStops] = useState<CourseStop[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    const q = district.trim();
    if (!q) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchCourse(q);
      setStops(result.stops);
    } catch (e) {
      setError(e instanceof Error ? e.message : "코스를 불러오지 못했어요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-sm px-4 py-6 pb-24">
      <h1 className="text-xl font-bold">💑 커플·여행 하루 코스</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        지역을 입력하면 브런치 → 점심 → 카페 → 저녁 → 술집 코스를 추천해요.
      </p>
      <div className="mt-4 flex gap-2">
        <input
          value={district}
          onChange={(e) => setDistrict(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") void run();
          }}
          placeholder="예: 강남구, 종로구"
          className="flex-1 rounded-xl border border-border px-4 py-3 text-sm"
        />
        <button
          type="button"
          onClick={() => void run()}
          className="rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white"
        >
          추천
        </button>
      </div>

      {loading ? (
        <p className="mt-6 text-sm text-muted-foreground">코스 짜는 중…</p>
      ) : error ? (
        <p className="mt-6 text-sm text-destructive">{error}</p>
      ) : stops ? (
        stops.length > 0 ? (
          <ol className="mt-6 space-y-3">
            {stops.map((s, i) => (
              <li
                key={s.slot}
                className="flex items-center gap-3 rounded-xl bg-muted p-4"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-white">
                  {i + 1}
                </span>
                <div>
                  <p className="text-xs text-muted-foreground">{s.slot}</p>
                  <p className="font-semibold">{s.name}</p>
                </div>
              </li>
            ))}
          </ol>
        ) : (
          <p className="mt-6 text-sm text-muted-foreground">
            해당 지역 코스를 찾지 못했어요. 다른 지역으로 시도해 보세요.
          </p>
        )
      ) : null}
    </main>
  );
}
