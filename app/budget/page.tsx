"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import {
  addExpense,
  currentMonthPeriod,
  dailyRemaining,
  fetchBudgetPlan,
  fetchBudgetReport,
  setBudget,
  type BudgetPlan,
  type BudgetReport,
} from "@/lib/gourmet-budget";

const won = (n: number) => `${n.toLocaleString("ko-KR")}원`;
const today = () => new Date().toISOString().slice(0, 10);

export default function BudgetPage() {
  const { user, ready } = useAuth();
  const [plan, setPlan] = useState<BudgetPlan | null>(null);
  const [report, setReport] = useState<BudgetReport | null>(null);
  const [budgetInput, setBudgetInput] = useState("");
  const [expenseInput, setExpenseInput] = useState("");
  const [expenseDate, setExpenseDate] = useState(today());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      setPlan(await fetchBudgetPlan(user.id));
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
      setPlan(await setBudget(user.id, Number(budgetInput), start, end));
      setBudgetInput("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "예산 설정 실패");
    }
  };

  const handleAddExpense = async () => {
    if (!user || !plan || !expenseInput) return;
    try {
      setPlan(await addExpense(user.id, plan.meal_plan_id, Number(expenseInput), expenseDate));
      setExpenseInput("");
      setReport(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "지출 입력 실패");
    }
  };

  const handleReport = async () => {
    if (!user || !plan) return;
    try {
      setReport(await fetchBudgetReport(user.id, plan.meal_plan_id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "리포트 실패");
    }
  };

  return (
    <main className="mx-auto max-w-sm px-4 py-6 pb-24">
      <h1 className="text-xl font-bold">💰 버짓</h1>

      {loading ? (
        <p className="mt-6 text-sm text-muted-foreground">불러오는 중…</p>
      ) : !plan ? (
        <section className="mt-6">
          <p className="text-sm text-muted-foreground">이번 달 식비 예산을 설정해 보세요.</p>
          <div className="mt-3 flex gap-2">
            <input
              type="number"
              inputMode="numeric"
              value={budgetInput}
              onChange={(e) => setBudgetInput(e.target.value)}
              placeholder="예: 500000"
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
                {won(plan.remaining)}
              </span>
            </div>
            <div className="mt-2 flex justify-between text-xs text-muted-foreground">
              <span>월 예산 {won(plan.monthly_budget)}</span>
              <span>지출 {won(plan.spent_amount)}</span>
            </div>
            <p className="mt-3 rounded-xl bg-card p-3 text-center text-sm">
              하루 사용 가능 <b>{won(dailyRemaining(plan))}</b>
            </p>
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
