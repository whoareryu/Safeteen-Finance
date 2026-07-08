"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import {
  addExpense,
  currentMonthPeriod,
  dailyRemaining,
  fetchAllBudgetPlans,
  fetchBudgetReport,
  setBudget,
  MEAL_TYPE_LABEL,
  type BudgetPlan,
  type BudgetReport,
  type MealType,
} from "@/lib/gourmet-budget";
import { cn } from "@/lib/utils";

const MEAL_TYPES: MealType[] = ["morning", "lunch", "dinner", "total"];

const won = (n: number) => `${n.toLocaleString("ko-KR")}원`;
const today = () => new Date().toISOString().slice(0, 10);

export default function BudgetPage() {
  const { user, ready } = useAuth();
  const [plans, setPlans] = useState<BudgetPlan[]>([]);
  const [selectedType, setSelectedType] = useState<MealType>("lunch");
  const [report, setReport] = useState<BudgetReport | null>(null);
  const [budgetInput, setBudgetInput] = useState("");
  const [expenseInput, setExpenseInput] = useState("");
  const [expenseDate, setExpenseDate] = useState(today());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const activePlan = plans.find((p) => p.meal_type === selectedType) ?? null;

  const reload = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      setPlans(await fetchAllBudgetPlans(user.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "불러오기 실패");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (ready && user) void reload();
    else if (ready) setLoading(false);
  }, [ready, user, reload]);

  useEffect(() => {
    setReport(null);
  }, [selectedType]);

  if (ready && !user) {
    return (
      <main className="mx-auto max-w-sm px-4 py-16 pb-24 text-center text-sm text-muted-foreground">
        버짓은 로그인 후 이용할 수 있어요.
      </main>
    );
  }

  const handleSetBudget = async () => {
    if (!user || !budgetInput) return;
    const { start, end } = currentMonthPeriod();
    try {
      const updated = await setBudget(user.id, Number(budgetInput), start, end, selectedType);
      setPlans((prev) => {
        const next = prev.filter((p) => p.meal_type !== selectedType);
        return [...next, updated];
      });
      setBudgetInput("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "예산 설정 실패");
    }
  };

  const handleAddExpense = async () => {
    if (!user || !activePlan || !expenseInput) return;
    try {
      const updated = await addExpense(user.id, activePlan.meal_plan_id, Number(expenseInput), expenseDate);
      setPlans((prev) => prev.map((p) => (p.meal_plan_id === updated.meal_plan_id ? updated : p)));
      setExpenseInput("");
      setReport(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "지출 입력 실패");
    }
  };

  const handleReport = async () => {
    if (!user || !activePlan) return;
    try {
      setReport(await fetchBudgetReport(user.id, activePlan.meal_plan_id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "리포트 실패");
    }
  };

  return (
    <main className="mx-auto max-w-sm px-4 py-6 pb-24">
      <h1 className="text-xl font-bold">💰 버짓</h1>

      {/* 식사 유형 탭 */}
      <div className="mt-4 flex gap-2">
        {MEAL_TYPES.map((type) => {
          const hasPlan = plans.some((p) => p.meal_type === type);
          return (
            <button
              key={type}
              type="button"
              onClick={() => setSelectedType(type)}
              className={cn(
                "flex-1 rounded-xl py-2 text-sm font-semibold transition",
                selectedType === type
                  ? "bg-primary text-white"
                  : "bg-muted text-foreground",
                hasPlan && selectedType !== type && "ring-1 ring-primary/40",
              )}
            >
              {MEAL_TYPE_LABEL[type]}
            </button>
          );
        })}
      </div>

      {loading ? (
        <p className="mt-6 text-sm text-muted-foreground">불러오는 중…</p>
      ) : !activePlan ? (
        <section className="mt-6">
          <p className="text-sm text-muted-foreground">
            이번 달 <b>{MEAL_TYPE_LABEL[selectedType]}</b> 예산을 설정해 보세요.
          </p>
          <p className="mt-1 text-xs text-muted-foreground">한 달 기준 금액으로 입력해 주세요.</p>
          <div className="mt-3 flex gap-2">
            <input
              type="number"
              inputMode="numeric"
              value={budgetInput}
              onChange={(e) => setBudgetInput(e.target.value)}
              placeholder="예: 300000"
              className="flex-1 rounded-xl border border-border px-4 py-3 text-sm"
            />
            <button
              type="button"
              onClick={() => void handleSetBudget()}
              className="rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white"
            >
              설정
            </button>
          </div>
        </section>
      ) : (
        <>
          <section className="mt-6 rounded-2xl bg-muted p-5">
            <div className="flex items-end justify-between">
              <span className="text-sm text-muted-foreground">남은 예산</span>
              <span className="text-2xl font-bold text-primary">
                {won(activePlan.remaining)}
              </span>
            </div>
            <div className="mt-2 flex justify-between text-xs text-muted-foreground">
              <span>월 예산 {won(activePlan.monthly_budget)}</span>
              <span>지출 {won(activePlan.spent_amount)}</span>
            </div>
            <p className="mt-3 rounded-xl bg-card p-3 text-center text-sm">
              하루 사용 가능 <b>{won(dailyRemaining(activePlan))}</b>
            </p>
            <button
              type="button"
              onClick={() => {
                setBudgetInput(String(activePlan.monthly_budget));
              }}
              className="mt-3 w-full text-center text-xs text-muted-foreground underline"
            >
              예산 수정
            </button>
            {budgetInput ? (
              <div className="mt-2 flex gap-2">
                <input
                  type="number"
                  inputMode="numeric"
                  value={budgetInput}
                  onChange={(e) => setBudgetInput(e.target.value)}
                  className="flex-1 rounded-xl border border-border px-3 py-2 text-sm"
                />
                <button
                  type="button"
                  onClick={() => void handleSetBudget()}
                  className="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
                >
                  저장
                </button>
                <button
                  type="button"
                  onClick={() => setBudgetInput("")}
                  className="rounded-xl bg-muted px-3 py-2 text-sm text-foreground"
                >
                  취소
                </button>
              </div>
            ) : null}
          </section>

          <section className="mt-5">
            <h2 className="text-sm font-semibold">지출 입력</h2>
            <div className="mt-2 flex gap-2">
              <input
                type="number"
                inputMode="numeric"
                value={expenseInput}
                onChange={(e) => setExpenseInput(e.target.value)}
                placeholder="금액"
                className="w-28 rounded-xl border border-border px-3 py-2.5 text-sm"
              />
              <input
                type="date"
                value={expenseDate}
                onChange={(e) => setExpenseDate(e.target.value)}
                className="flex-1 rounded-xl border border-border px-3 py-2.5 text-sm"
              />
              <button
                type="button"
                onClick={() => void handleAddExpense()}
                className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white"
              >
                추가
              </button>
            </div>
          </section>

          <section className="mt-5">
            <button
              type="button"
              onClick={() => void handleReport()}
              className="w-full rounded-xl bg-muted py-3 text-sm font-semibold text-foreground"
            >
              📊 월말 리포트 보기
            </button>
            {report ? (
              <div className="mt-3 space-y-3 rounded-2xl bg-muted p-5 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">총 지출</span>
                  <b>{won(report.total_spent)}</b>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">절약 금액</span>
                  <b className="text-primary">{won(report.saved_amount)}</b>
                </div>
                {report.top_restaurants.length > 0 ? (
                  <div>
                    <p className="text-muted-foreground">자주 간 식당</p>
                    <ul className="mt-1 space-y-1">
                      {report.top_restaurants.map((r, i) => (
                        <li key={i} className="flex justify-between">
                          <span>{r.name}</span>
                          <span className="text-muted-foreground">
                            {won(r.total)} · {r.visits}회
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {report.top_categories.length > 0 ? (
                  <div>
                    <p className="text-muted-foreground">선호 음식</p>
                    <ul className="mt-1 space-y-1">
                      {report.top_categories.map((c, i) => (
                        <li key={i} className="flex justify-between">
                          <span>{c.label}</span>
                          <span className="text-muted-foreground">{won(c.total)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>
            ) : null}
          </section>
        </>
      )}

      {error ? <p className="mt-4 text-sm text-destructive">{error}</p> : null}
    </main>
  );
}
