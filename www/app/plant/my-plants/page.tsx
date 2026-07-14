"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Camera, Loader2, Plus, Upload } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { registerMyPlant, listMyPlants, type MyPlant } from "@/lib/my-plants-api";
import { cn } from "@/lib/utils";

const STAGE_EMOJI: Record<string, string> = {
  새싹: "🌱",
  새순: "🌿",
  성목: "🌳",
};

export default function MyPlantsPage() {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const [plants, setPlants] = useState<MyPlant[]>([]);
  const [loadingList, setLoadingList] = useState(true);

  const [speciesName, setSpeciesName] = useState("");
  const [region, setRegion] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoadingList(true);
    try {
      const list = await listMyPlants(user?.id);
      setPlants(list);
    } catch {
      setPlants([]);
    } finally {
      setLoadingList(false);
    }
  }, [user?.id]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const submit = async () => {
    if (!region.trim() || (!speciesName.trim() && !photo)) {
      setError("장소는 필수이고, 종류 입력 또는 사진 중 하나는 있어야 해요.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await registerMyPlant({
        region: region.trim(),
        speciesName: speciesName.trim() || undefined,
        photo: photo ?? undefined,
        ownerUserId: user?.id,
      });
      setSpeciesName("");
      setRegion("");
      setPhoto(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "등록에 실패했어요.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-foreground">마이플랜트</h1>
        <Link href="/plant/leaderboard" className="text-sm font-medium text-primary underline underline-offset-4">
          랭킹 보기 →
        </Link>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">
        내 반려식물을 등록하고, 매일 사진으로 출석체크하며 식물집사 포인트를 모아보세요.
      </p>

      <div className="mt-6 rounded-2xl border border-border bg-card p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-foreground">새 식물 등록</h2>

        <label className="mt-3 block text-sm font-medium text-foreground">
          키우는 장소
          <input
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            placeholder="예: 거실, 베란다"
            className="mt-1 block w-full rounded-lg border border-border bg-input px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
          />
        </label>

        <label className="mt-3 block text-sm font-medium text-foreground">
          종류 (사진으로 등록하면 생략 가능)
          <input
            value={speciesName}
            onChange={(e) => setSpeciesName(e.target.value)}
            placeholder="예: 몬스테라"
            className="mt-1 block w-full rounded-lg border border-border bg-input px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
          />
        </label>

        <div className="mt-3 flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => setPhoto(e.target.files?.[0] ?? null)}
          />
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => setPhoto(e.target.files?.[0] ?? null)}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-muted"
          >
            <Upload className="h-3.5 w-3.5" aria-hidden />
            사진 선택
          </button>
          <button
            type="button"
            onClick={() => cameraInputRef.current?.click()}
            className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-muted"
          >
            <Camera className="h-3.5 w-3.5" aria-hidden />
            촬영하기
          </button>
          {photo && <span className="truncate text-xs text-muted-foreground">{photo.name}</span>}
        </div>

        {error && <p className="mt-3 text-sm text-destructive">{error}</p>}

        <button
          type="button"
          onClick={() => void submit()}
          disabled={submitting}
          className={cn(
            "mt-4 inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:opacity-50"
          )}
        >
          {submitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              등록 중…
            </>
          ) : (
            <>
              <Plus className="h-4 w-4" aria-hidden />
              등록하기
            </>
          )}
        </button>
      </div>

      <h2 className="mt-8 text-sm font-semibold text-foreground">내 식물 목록</h2>
      {loadingList ? (
        <p className="mt-3 text-sm text-muted-foreground">불러오는 중…</p>
      ) : plants.length === 0 ? (
        <p className="mt-3 text-sm text-muted-foreground">아직 등록한 식물이 없어요.</p>
      ) : (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          {plants.map((p) => (
            <Link
              key={p.id}
              href={`/plant/my-plants/${p.id}`}
              className="rounded-2xl border border-border bg-card p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="flex items-center justify-between">
                <span className="text-2xl" aria-hidden>
                  {STAGE_EMOJI[p.growth_stage] ?? "🌱"}
                </span>
                <span className="rounded-full bg-accent px-2 py-0.5 text-xs font-medium text-accent-foreground">
                  {p.growth_stage}
                </span>
              </div>
              <p className="mt-2 font-semibold text-foreground">{p.nickname}</p>
              <p className="text-xs text-muted-foreground">
                {p.species_name} · {p.region}
              </p>
              <p className="mt-2 text-xs text-muted-foreground">
                {p.points}P · 🔥 {p.streak_count}일 연속
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
