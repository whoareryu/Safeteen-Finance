"use client";

import { useEffect, useState } from "react";
import MypageShell from "@/components/mypage-shell";
import { useAuth } from "@/components/auth-provider";
import { authHeaders } from "@/lib/auth";

type MealPlan = {
  id: number;
  monthly_budget: number;
  spent_amount: number;
  period_start: string;
  period_end: string;
  remaining_budget: number;
};

function defaultPeriod() {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  const fmt = (d: Date) => d.toISOString().slice(0, 10);
  return { start: fmt(start), end: fmt(end) };
}

export default function MypageBudgetPage() {
  const { user } = useAuth();
  const defaults = defaultPeriod();
  const [monthlyBudget, setMonthlyBudget] = useState("300000");
  const [spentAmount, setSpentAmount] = useState("0");
  const [periodStart, setPeriodStart] = useState(defaults.start);
  const [periodEnd, setPeriodEnd] = useState(defaults.end);
  const [plan, setPlan] = useState<MealPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.id) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/gourmet/meal-plans/me/current`, {
          headers: authHeaders(user),
        });
        if (res.status === 404) {
          if (!cancelled) setPlan(null);
          return;
        }
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(
            typeof body.detail === "string" ? body.detail : "플랜을 불러오지 못했습니다."
          );
        }
        const data = (await res.json()) as MealPlan;
        if (!cancelled) {
          setPlan(data);
          setMonthlyBudget(String(data.monthly_budget));
          setSpentAmount(String(data.spent_amount));
          setPeriodStart(data.period_start);
          setPeriodEnd(data.period_end);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "오류");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user?.id]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.id) {
      setError("다시 로그인해 주세요. (계정 정보 갱신 필요)");
      return;
    }
    setSaving(true);
    setMessage(null);
    setError(null);
    try {
      const res = await fetch(`/api/gourmet/meal-plans/me/current`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders(user) },
        body: JSON.stringify({
          monthly_budget: Number(monthlyBudget),
          spent_amount: Number(spentAmount),
          period_start: periodStart,
          period_end: periodEnd,
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(
          typeof body.detail === "string" ? body.detail : "저장에 실패했습니다."
        );
      }
      const data = (await res.json()) as MealPlan;
      setPlan(data);
      setMessage("식비 플랜이 저장되었습니다.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "저장 오류");
    } finally {
      setSaving(false);
    }
  };

  if (user && typeof user.id !== "number") {
    return (
      <MypageShell title="버짓설정">
        <p className="text-sm text-amber-800">
          계정 정보가 오래되었습니다. 로그아웃 후 다시 로그인해 주세요.
        </p>
      </MypageShell>
    );
  }

  return (
    <MypageShell title="버짓설정">
      {loading ? (
        <p className="text-sm text-[#6e6e73]">불러오는 중…</p>
      ) : (
        <form
          onSubmit={handleSave}
          className="max-w-lg space-y-6 rounded-2xl border border-black/10 bg-white p-6 shadow-sm"
        >
          <p className="text-sm text-[#6e6e73]">
            한 달 목표 식비와 지출액을 설정하면 예산에 맞는 맛집 추천에 활용할 수
            있습니다.
          </p>

          {plan ? (
            <p className="rounded-lg bg-[#f5f5f7] px-4 py-3 text-sm">
              잔여 예산:{" "}
              <strong>{plan.remaining_budget.toLocaleString()}원</strong>
            </p>
          ) : null}

          <label className="block text-sm">
            <span className="font-medium text-[#1d1d1f]">월 목표 식비 (원)</span>
            <input
              type="number"
              min={0}
              step={10000}
              value={monthlyBudget}
              onChange={(e) => setMonthlyBudget(e.target.value)}
              className="mt-1 w-full rounded-lg border border-black/15 px-3 py-2"
              required
            />
          </label>

          <label className="block text-sm">
            <span className="font-medium text-[#1d1d1f]">현재까지 지출 (원)</span>
            <input
              type="number"
              min={0}
              step={1000}
              value={spentAmount}
              onChange={(e) => setSpentAmount(e.target.value)}
              className="mt-1 w-full rounded-lg border border-black/15 px-3 py-2"
              required
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm">
              <span className="font-medium text-[#1d1d1f]">시작일</span>
              <input
                type="date"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
                className="mt-1 w-full rounded-lg border border-black/15 px-3 py-2"
                required
              />
            </label>
            <label className="block text-sm">
              <span className="font-medium text-[#1d1d1f]">종료일</span>
              <input
                type="date"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
                className="mt-1 w-full rounded-lg border border-black/15 px-3 py-2"
                required
              />
            </label>
          </div>

          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          {message ? <p className="text-sm text-green-700">{message}</p> : null}

          <button
            type="submit"
            disabled={saving}
            className="rounded-full bg-[#1d1d1f] px-6 py-2.5 text-sm font-medium text-white disabled:opacity-50"
          >
            {saving ? "저장 중…" : "저장"}
          </button>
        </form>
      )}
    </MypageShell>
  );
}
