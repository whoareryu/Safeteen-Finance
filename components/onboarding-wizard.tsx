"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, ChevronUp } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { submitOnboarding } from "@/lib/gourmet-onboarding";
import { cn } from "@/lib/utils";

const TOTAL_STEPS = 5;

const DINING_OPTIONS = [
  { value: "dine_in", label: "외식" },
  { value: "delivery", label: "배달" },
  { value: "pickup", label: "픽업" },
] as const;

const PORTION_OPTIONS = [
  { value: "under_one", label: "1인분 이하" },
  { value: "one", label: "1인분" },
  { value: "one_half", label: "1.5인분" },
  { value: "two_plus", label: "2인분 이상" },
] as const;

const INITIAL_GENRES = ["한식", "중식", "일식", "양식", "분식", "아시안"];

// 진행바 너비 (step 인덱스: 1~5). 인라인 style 금지 → 정적 Tailwind 클래스.
const STEP_WIDTH: Record<number, string> = {
  1: "w-1/5",
  2: "w-2/5",
  3: "w-3/5",
  4: "w-4/5",
  5: "w-full",
};

function toList(raw: string): string[] {
  return raw
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
}

export default function OnboardingWizard() {
  const { user, ready } = useAuth();
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [genres, setGenres] = useState<string[]>(INITIAL_GENRES);
  const [diningMode, setDiningMode] = useState("dine_in");
  const [portion, setPortion] = useState("one");
  const [allergies, setAllergies] = useState("");
  const [avoidFoods, setAvoidFoods] = useState("");
  const [useBudget, setUseBudget] = useState(false);
  const [monthlyBudget, setMonthlyBudget] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (ready && !user) {
    return (
      <div className="mx-auto max-w-sm px-4 py-16 text-center text-sm text-muted-foreground">
        온보딩은 로그인 후 이용할 수 있어요.
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
        dining_mode: diningMode,
        portion,
        allergies: toList(allergies),
        avoid_foods: toList(avoidFoods),
        use_budget: useBudget,
        monthly_budget: useBudget && monthlyBudget ? Number(monthlyBudget) : null,
      });
      router.replace("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "저장에 실패했어요.");
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[calc(100dvh-var(--site-header-height))] max-w-sm flex-col px-4 py-6">
      {/* 프로그레스바 */}
      <div className="mb-6">
        <div className="mb-1 flex justify-between text-xs text-muted-foreground">
          <span>
            {step} / {TOTAL_STEPS}
          </span>
          <span>{Math.round((step / TOTAL_STEPS) * 100)}%</span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <div
            className={cn(
              "h-full rounded-full bg-primary transition-all",
              STEP_WIDTH[step],
            )}
          />
        </div>
      </div>

      <div className="flex-1">
        {step === 1 ? (
          <section>
            <h2 className="text-lg font-bold">음식 장르 선호 순위</h2>
            <p className="mt-1 text-sm text-muted-foreground">위일수록 더 좋아하는 장르예요.</p>
            <ul className="mt-4 space-y-2">
              {genres.map((g, i) => (
                <li
                  key={g}
                  className="flex items-center justify-between rounded-xl bg-muted px-4 py-3"
                >
                  <span className="text-sm font-medium">
                    {i + 1}. {g}
                  </span>
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
            title="식사 방식"
            options={DINING_OPTIONS}
            value={diningMode}
            onSelect={setDiningMode}
          />
        ) : null}

        {step === 3 ? (
          <Choices
            title="평소 식사량"
            options={PORTION_OPTIONS}
            value={portion}
            onSelect={setPortion}
          />
        ) : null}

        {step === 4 ? (
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

        {step === 5 ? (
          <section>
            <h2 className="text-lg font-bold">버짓 서비스</h2>
            <div className="mt-4 flex gap-2">
              <button
                type="button"
                onClick={() => setUseBudget(true)}
                className={cn(
                  "flex-1 rounded-xl py-3 text-sm font-semibold",
                  useBudget ? "bg-primary text-white" : "bg-muted text-foreground",
                )}
              >
                사용할게요
              </button>
              <button
                type="button"
                onClick={() => setUseBudget(false)}
                className={cn(
                  "flex-1 rounded-xl py-3 text-sm font-semibold",
                  !useBudget ? "bg-primary text-white" : "bg-muted text-foreground",
                )}
              >
                안 쓸게요
              </button>
            </div>
            {useBudget ? (
              <div className="mt-4">
                <label className="block text-sm font-medium">월 예산 (원)</label>
                <input
                  type="number"
                  inputMode="numeric"
                  value={monthlyBudget}
                  onChange={(e) => setMonthlyBudget(e.target.value)}
                  placeholder="예: 500000"
                  className="mt-1 w-full rounded-xl border border-border px-4 py-3 text-sm"
                />
                <p className="mt-2 rounded-xl bg-muted p-3 text-xs leading-relaxed text-muted-foreground">
                  한달 점심 비용 50만원으로 적용 시, 매일 한달 동안 비용을 나눠서
                  점심에 사용할 수 있는 금액에 맞는 식당을 추천해주는 서비스입니다.
                </p>
              </div>
            ) : null}
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
            {submitting ? "저장 중…" : "시작하기"}
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
                value === opt.value
                  ? "bg-primary text-white"
                  : "bg-muted text-foreground",
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
