"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { Camera, Loader2, Upload } from "lucide-react";
import {
  checkinMyPlant,
  getMyPlant,
  listBadges,
  listCheckins,
  type Badge,
  type CheckinHistoryItem,
  type MyPlant,
} from "@/lib/my-plants-api";
import { cn } from "@/lib/utils";

const STAGE_EMOJI: Record<string, string> = {
  새싹: "🌱",
  새순: "🌿",
  성목: "🌳",
};

const STAGE_ORDER = ["새싹", "새순", "성목"];

export default function MyPlantDetailPage() {
  const params = useParams<{ id: string }>();
  const plantId = Number(params.id);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const [plant, setPlant] = useState<MyPlant | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [history, setHistory] = useState<CheckinHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkingIn, setCheckingIn] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [p, b, h] = await Promise.all([
        getMyPlant(plantId),
        listBadges(plantId),
        listCheckins(plantId),
      ]);
      setPlant(p);
      setBadges(b);
      setHistory(h);
    } catch (e) {
      setError(e instanceof Error ? e.message : "정보를 불러오지 못했어요.");
    } finally {
      setLoading(false);
    }
  }, [plantId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleCheckin = async (file: File | null) => {
    if (!file || checkingIn) return;
    setCheckingIn(true);
    setError(null);
    setMessage(null);
    try {
      const result = await checkinMyPlant(plantId, file);
      const badgeText =
        result.new_badges.length > 0
          ? ` 🎉 새 뱃지 획득: ${result.new_badges.join(", ")}`
          : "";
      setMessage(
        `출석 완료! 건강도 ${result.health_score}점, +${result.points_earned}P (연속 ${result.streak_day}일)${badgeText}`
      );
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "출석체크에 실패했어요.");
    } finally {
      setCheckingIn(false);
    }
  };

  if (loading) {
    return <p className="mx-auto max-w-2xl px-6 py-10 text-sm text-muted-foreground">불러오는 중…</p>;
  }

  if (!plant) {
    return <p className="mx-auto max-w-2xl px-6 py-10 text-sm text-destructive">{error ?? "식물을 찾을 수 없어요."}</p>;
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <div className="rounded-2xl border border-border bg-card p-6 text-center shadow-sm">
        <span className="text-5xl" aria-hidden>
          {STAGE_EMOJI[plant.growth_stage] ?? "🌱"}
        </span>
        <h1 className="mt-2 text-xl font-semibold text-foreground">{plant.nickname}</h1>
        <p className="text-sm text-muted-foreground">
          {plant.species_name} · {plant.region}
        </p>

        <div className="mt-4 flex justify-center gap-2">
          {STAGE_ORDER.map((stage) => (
            <span
              key={stage}
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium",
                stage === plant.growth_stage
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              )}
            >
              {STAGE_EMOJI[stage]} {stage}
            </span>
          ))}
        </div>

        <div className="mt-4 flex justify-center gap-6 text-sm">
          <div>
            <p className="text-lg font-semibold text-foreground">{plant.points}</p>
            <p className="text-xs text-muted-foreground">포인트</p>
          </div>
          <div>
            <p className="text-lg font-semibold text-foreground">🔥 {plant.streak_count}</p>
            <p className="text-xs text-muted-foreground">연속 출석</p>
          </div>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-border bg-card p-5 text-center shadow-sm">
        <h2 className="text-sm font-semibold text-foreground">오늘의 출석체크</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          오늘 식물 사진을 찍어서 올리면 건강도에 따라 포인트를 받아요.
        </p>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            void handleCheckin(e.target.files?.[0] ?? null);
            e.target.value = "";
          }}
        />
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={(e) => {
            void handleCheckin(e.target.files?.[0] ?? null);
            e.target.value = "";
          }}
        />

        <div className="mt-3 flex justify-center gap-2">
          <button
            type="button"
            disabled={checkingIn}
            onClick={() => cameraInputRef.current?.click()}
            className="inline-flex items-center gap-1.5 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
          >
            {checkingIn ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : <Camera className="h-4 w-4" aria-hidden />}
            사진 찍기
          </button>
          <button
            type="button"
            disabled={checkingIn}
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground disabled:opacity-50"
          >
            <Upload className="h-4 w-4" aria-hidden />
            앨범에서 선택
          </button>
        </div>

        {message && <p className="mt-3 text-sm text-primary">{message}</p>}
        {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
      </div>

      <h2 className="mt-8 text-sm font-semibold text-foreground">뱃지</h2>
      <div className="mt-3 grid grid-cols-3 gap-2 sm:grid-cols-6">
        {badges.map((b) => (
          <div
            key={b.code}
            title={b.description}
            className={cn(
              "flex flex-col items-center gap-1 rounded-xl border p-2 text-center",
              b.earned ? "border-primary bg-accent" : "border-border bg-muted/40 opacity-40"
            )}
          >
            <span className="text-xl" aria-hidden>
              {b.icon}
            </span>
            <span className="text-[10px] text-foreground">{b.name}</span>
          </div>
        ))}
      </div>

      <h2 className="mt-8 text-sm font-semibold text-foreground">출석체크 이력</h2>
      {history.length === 0 ? (
        <p className="mt-3 text-sm text-muted-foreground">아직 출석체크 기록이 없어요.</p>
      ) : (
        <div className="mt-3 space-y-2">
          {history.map((h) => (
            <div
              key={h.id}
              className="flex items-center justify-between rounded-xl border border-border bg-card px-4 py-2.5 text-sm"
            >
              <span className="text-muted-foreground">{h.checkin_date}</span>
              <span className="text-foreground">건강도 {h.health_score}</span>
              <span className="font-medium text-primary">+{h.points_earned}P</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
