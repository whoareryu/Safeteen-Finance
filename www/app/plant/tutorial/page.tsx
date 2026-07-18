"use client";

import { useCallback, useEffect, useState } from "react";
import { Droplets, Leaf, Sprout, Sun } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import AuthModal from "@/components/auth-modal";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import {
  TUTORIAL_REGIONS,
  TUTORIAL_SPECIES,
  addNutrientTutorialPlant,
  checkLeavesTutorialPlant,
  createTutorialPlant,
  getActiveTutorialPlant,
  moveLightTutorialPlant,
  waterTutorialPlant,
  type TutorialState,
} from "@/lib/plant-tutorial-api";

const LIGHT_POSITIONS = ["음지", "반양지", "양지"] as const;

export default function TutorialPage() {
  const { user, ready } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  const [loading, setLoading] = useState(true);
  const [tutorial, setTutorial] = useState<TutorialState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const [selectedSpecies, setSelectedSpecies] = useState<string | null>(null);
  const [selectedRegion, setSelectedRegion] = useState("서울");

  useEffect(() => {
    if (!ready || !user) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    getActiveTutorialPlant(user.id)
      .then((state) => {
        if (!cancelled) setTutorial(state);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "불러오기에 실패했습니다.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [ready, user]);

  const startTutorial = useCallback(async () => {
    if (!user || !selectedSpecies || actionLoading) return;
    setActionLoading(true);
    setError(null);
    try {
      const state = await createTutorialPlant(selectedSpecies, selectedRegion, user.id);
      setTutorial(state);
    } catch (e) {
      setError(e instanceof Error ? e.message : "식물을 심는 데 실패했습니다.");
    } finally {
      setActionLoading(false);
    }
  }, [user, selectedSpecies, selectedRegion, actionLoading]);

  const runAction = useCallback(
    async (action: () => Promise<TutorialState>) => {
      if (actionLoading) return;
      setActionLoading(true);
      setError(null);
      try {
        const state = await action();
        setTutorial(state);
      } catch (e) {
        setError(e instanceof Error ? e.message : "요청에 실패했습니다.");
      } finally {
        setActionLoading(false);
      }
    },
    [actionLoading]
  );

  if (!ready || loading) {
    return (
      <div className="mx-auto max-w-2xl px-6 pb-28 pt-10">
        <p className="text-sm text-muted-foreground">불러오는 중…</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-2xl px-6 pb-28 pt-10">
        <h1 className="text-xl font-semibold text-foreground">식집사 튜토리얼</h1>
        <div className="saessak-card mt-6 flex flex-col items-center gap-3 px-6 py-10 text-center">
          <Sprout className="h-10 w-10 text-primary" aria-hidden />
          <p className="text-sm text-muted-foreground">
            로그인하면 가상 식물을 키우며 물주기·영양제·햇빛 관리를 연습할 수 있어요.
          </p>
          <button
            type="button"
            onClick={() => setShowAuthModal(true)}
            className="mt-2 inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition hover:opacity-90"
          >
            로그인하고 시작하기
          </button>
        </div>
        <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} initialView="login" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 pb-28 pt-10">
      <h1 className="text-xl font-semibold text-foreground">식집사 튜토리얼</h1>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        실제 식물을 죽일까 걱정된다면, 여기서 먼저 연습해보세요. 날씨에 따라 흙 상태가 실제로 변해요.
      </p>

      {error && (
        <p className="mt-4 rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}

      {tutorial ? (
        <TutorialGameView tutorial={tutorial} actionLoading={actionLoading} runAction={runAction} />
      ) : (
        <div className="mt-6">
          <p className="text-sm font-medium text-foreground">키우고 싶은 식물을 골라주세요</p>
          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {TUTORIAL_SPECIES.map((species) => (
              <button
                key={species.name}
                type="button"
                onClick={() => setSelectedSpecies(species.name)}
                className={cn(
                  "flex flex-col items-center gap-2 rounded-2xl border px-3 py-5 text-sm transition",
                  selectedSpecies === species.name
                    ? "border-primary bg-primary/5 font-medium text-primary"
                    : "border-border bg-card text-foreground hover:border-primary/40"
                )}
              >
                <Leaf className="h-6 w-6" aria-hidden />
                {species.label}
              </button>
            ))}
          </div>

          <label className="mt-5 block text-sm font-medium text-foreground">
            지역 (날씨 연동용)
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-border bg-input px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
            >
              {TUTORIAL_REGIONS.map((region) => (
                <option key={region} value={region}>
                  {region}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            onClick={() => void startTutorial()}
            disabled={!selectedSpecies || actionLoading}
            className="mt-5 inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:opacity-50"
          >
            {actionLoading ? "심는 중…" : "심기 시작"}
          </button>
        </div>
      )}
    </div>
  );
}

function TutorialGameView({
  tutorial,
  actionLoading,
  runAction,
}: {
  tutorial: TutorialState;
  actionLoading: boolean;
  runAction: (action: () => Promise<TutorialState>) => Promise<void>;
}) {
  return (
    <div className="mt-6">
      <div className="saessak-card overflow-hidden">
        {tutorial.photo_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={tutorial.photo_url}
            alt={`${tutorial.species_name} 상태 사진`}
            className="h-56 w-full object-cover"
          />
        ) : (
          <div className="flex h-56 w-full items-center justify-center bg-muted/40">
            <Leaf className="h-12 w-12 text-muted-foreground" aria-hidden />
          </div>
        )}
        <div className="px-4 py-3">
          <p className="text-sm font-semibold text-foreground">
            {tutorial.species_name} · {tutorial.growth_stage} · {tutorial.points}P
          </p>
          <p className="mt-0.5 text-xs text-muted-foreground">
            {tutorial.region} · 현재 자리: {tutorial.light_position}
          </p>
        </div>
      </div>

      {tutorial.feedback && (
        <p className="mt-3 rounded-xl bg-primary/10 px-4 py-3 text-sm text-primary" role="status">
          {tutorial.feedback}
        </p>
      )}

      <div className="saessak-card mt-4 space-y-3 px-4 py-4">
        <div>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>수분</span>
            <span>{Math.round(tutorial.soil_moisture_pct)}%</span>
          </div>
          <Progress value={tutorial.soil_moisture_pct} className="mt-1" />
        </div>
        <div>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>영양</span>
            <span>{Math.round(tutorial.nutrient_pct)}%</span>
          </div>
          <Progress value={tutorial.nutrient_pct} className="mt-1" />
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <button
          type="button"
          disabled={actionLoading}
          onClick={() => void runAction(() => waterTutorialPlant(tutorial.id))}
          className="flex items-center justify-center gap-2 rounded-full bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:opacity-50"
        >
          <Droplets className="h-4 w-4" aria-hidden />
          물주기
        </button>
        <button
          type="button"
          disabled={actionLoading}
          onClick={() => void runAction(() => addNutrientTutorialPlant(tutorial.id))}
          className="flex items-center justify-center gap-2 rounded-full border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground transition hover:bg-secondary disabled:opacity-50"
        >
          <Sprout className="h-4 w-4" aria-hidden />
          영양제
        </button>
        <button
          type="button"
          disabled={actionLoading}
          onClick={() => void runAction(() => checkLeavesTutorialPlant(tutorial.id))}
          className="flex items-center justify-center gap-2 rounded-full border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground transition hover:bg-secondary disabled:opacity-50"
        >
          <Leaf className="h-4 w-4" aria-hidden />
          잎사귀 확인
        </button>
        <div className="flex items-center gap-1 rounded-full border border-border bg-card p-1">
          {LIGHT_POSITIONS.map((position) => (
            <button
              key={position}
              type="button"
              disabled={actionLoading}
              onClick={() => void runAction(() => moveLightTutorialPlant(tutorial.id, position))}
              className={cn(
                "flex flex-1 items-center justify-center gap-1 rounded-full px-2 py-1.5 text-xs font-medium transition disabled:opacity-50",
                tutorial.light_position === position
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-secondary"
              )}
            >
              <Sun className="h-3.5 w-3.5" aria-hidden />
              {position}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
