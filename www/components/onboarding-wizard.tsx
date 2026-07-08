"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, ChevronUp } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import {
  fetchMyPreference,
  markOnboardingDone,
  submitOnboarding,
} from "@/lib/gourmet-onboarding";
import { cn } from "@/lib/utils";

const TOTAL_STEPS = 3;

const PORTION_OPTIONS = [
  { value: "under_one", label: "1인분 이하" },
  { value: "one", label: "1인분" },
  { value: "one_half", label: "1.5인분" },
  { value: "two_plus", label: "2인분 이상" },
] as const;

const INITIAL_GENRES = ["한식", "중식", "일식", "양식", "분식", "아시안"];

const STEP_WIDTH: Record<number, string> = {
  1: "w-1/3",
  2: "w-2/3",
  3: "w-full",
};

function toList(raw: string): string[] {
  return raw.split(",").map((x) => x.trim()).filter(Boolean);
}

export default function OnboardingWizard({ editMode = false }: { editMode?: boolean }) {
  const { user, ready } = useAuth();
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [genres, setGenres] = useState<string[]>(INITIAL_GENRES);
  const [portion, setPortion] = useState("one");
  const [allergies, setAllergies] = useState("");
  const [avoidFoods, setAvoidFoods] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prefetched, setPrefetched] = useState(!editMode);

  // 편집 모드: 기존 선호도 불러와서 초기값으로 채움
  useEffect(() => {
    if (!editMode || !user) return;
    fetchMyPreference(user.id)
      .then((pref) => {
        if (pref.genre_ranking?.length) setGenres(pref.genre_ranking);
        if (pref.portion) setPortion(pref.portion);
        if (pref.allergies?.length) setAllergies(pref.allergies.join(", "));
        if (pref.avoid_foods?.length) setAvoidFoods(pref.avoid_foods.join(", "));
        setPrefetched(true);
      })
      .catch(() => setPrefetched(true));
  }, [editMode, user]);

  if (ready && !user) {
    return (
      <div className="mx-auto max-w-sm px-4 py-16 text-center text-sm text-muted-foreground">
        온보딩은 로그인 후 이용할 수 있어요.
      </div>
    );
  }

  if (!prefetched) {
    return (
      <div className="mx-auto max-w-sm px-4 py-16 text-center text-sm text-muted-foreground">
        불러오는 중…
      </div>
    );
  }

  const moveGenre = (index: number, dir: -1 | 1) => {
    setGenres((prev) => {
      const next = [...prev];
      const j = index + dir;
      if (j < 0 || j >= next.length) return prev;
      const tmp = next[index];
      next[index] = next[j];
      next[j] = tmp;
      return next;
    });
  };

  const handleSubmit = async () => {
    if (!user) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitOnboarding(user.id, {
        genre_ranking: genres,
        dining_mode: "dine_in",
        portion,
        allergies: toList(allergies),
        avoid_foods: toList(avoidFoods),
        use_budget: false,
        monthly_budget: null,
      });
      markOnboardingDone(user.id);
      router.replace(editMode ? "/mypage" : "/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "저장에 실패했어요.");
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[calc(100dvh-var(--site-header-height))] max-w-sm flex-col px-4 pt-6 pb-24">
      {/* 프로그레스바 */}
      <div className="mb-6">
        <div className="mb-1 flex justify-between text-xs text-muted-foreground">
          <span>{step} / {TOTAL_STEPS}</span>
          <span>{Math.round((step / TOTAL_STEPS) * 100)}%</span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <div className={cn("h-full rounded-full bg-primary transition-all", STEP_WIDTH[step])} />
        </div>
      </div>

      <div className="flex-1">
        {step === 1 ? (
          <section>
            <h2 className="text-lg font-bold">음식 장르 선호 순위</h2>
            <p className="mt-1 text-sm text-muted-foreground">위일수록 더 좋아하는 장르예요.</p>
            <ul className="mt-4 space-y-2">
              {genres.map((g, i) => (
                <li key={g} className="flex items-center justify-between rounded-xl bg-muted px-4 py-3">
                  <span className="text-sm font-medium">{i + 1}. {g}</span>
                  <span className="flex gap-1">
                    <button
                      type="button"
                      aria-label="위로"
                      disabled={i === 0}
                      onClick={() => moveGenre(i, -1)}
                      className="rounded-lg bg-card p-1 text-muted-foreground shadow-sm disabled:opacity-30"
                    >
                      <ChevronUp className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      aria-label="아래로"
                      disabled={i === genres.length - 1}
                      onClick={() => moveGenre(i, 1)}
                      className="rounded-lg bg-card p-1 text-muted-foreground shadow-sm disabled:opacity-30"
                    >
                      <ChevronDown className="h-4 w-4" />
                    </button>
                  </span>
                </li>
              ))}
            </ul>
          </section>
        ) : null}

        {step === 2 ? (
          <Choices
            title="평소 식사량"
            options={PORTION_OPTIONS}
            value={portion}
            onSelect={setPortion}
          />
        ) : null}

        {step === 3 ? (
          <section>
            <h2 className="text-lg font-bold">알레르기 · 기피 음식</h2>
            <p className="mt-1 text-sm text-muted-foreground">선택 입력이에요. 쉼표로 구분해 주세요.</p>
            <label className="mt-4 block text-sm font-medium">알레르기</label>
            <input
              value={allergies}
              onChange={(e) => setAllergies(e.target.value)}
              placeholder="예: 땅콩, 갑각류"
              className="mt-1 w-full rounded-xl border border-border px-4 py-3 text-sm"
            />
            <label className="mt-4 block text-sm font-medium">기피 음식</label>
            <input
              value={avoidFoods}
              onChange={(e) => setAvoidFoods(e.target.value)}
              placeholder="예: 오이, 양고기"
              className="mt-1 w-full rounded-xl border border-border px-4 py-3 text-sm"
            />
          </section>
        ) : null}
      </div>

      {error ? <p className="mt-3 text-sm text-destructive">{error}</p> : null}

      <div className="mt-6 flex gap-2">
        {step > 1 ? (
          <button
            type="button"
            onClick={() => setStep((s) => s - 1)}
            className="rounded-xl bg-muted px-5 py-3 text-sm font-semibold text-foreground"
          >
            이전
          </button>
        ) : null}
        {step < TOTAL_STEPS ? (
          <button
            type="button"
            onClick={() => setStep((s) => s + 1)}
            className="flex-1 rounded-xl bg-primary py-3 text-sm font-semibold text-white"
          >
            다음
          </button>
        ) : (
          <button
            type="button"
            onClick={() => void handleSubmit()}
            disabled={submitting}
            className="flex-1 rounded-xl bg-primary py-3 text-sm font-semibold text-white disabled:opacity-50"
          >
            {submitting ? "저장 중…" : editMode ? "저장하기" : "시작하기"}
          </button>
        )}
      </div>
    </div>
  );
}

function Choices({
  title,
  options,
  value,
  onSelect,
}: {
  title: string;
  options: ReadonlyArray<{ value: string; label: string }>;
  value: string;
  onSelect: (value: string) => void;
}) {
  return (
    <section>
      <h2 className="text-lg font-bold">{title}</h2>
      <ul className="mt-4 space-y-2">
        {options.map((opt) => (
          <li key={opt.value}>
            <button
              type="button"
              onClick={() => onSelect(opt.value)}
              className={cn(
                "w-full rounded-xl px-4 py-3 text-left text-sm font-medium",
                value === opt.value ? "bg-primary text-white" : "bg-muted text-foreground",
              )}
            >
              {opt.label}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
