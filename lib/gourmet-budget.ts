/** 버짓(식비) API 래퍼 (백엔드 /gourmet/budget, X-User-Id 인증). */

function userHeader(userId: number): Record<string, string> {
  return { "X-User-Id": String(userId) };
}

export type MealType = "total" | "morning" | "lunch" | "dinner";

export const MEAL_TYPE_LABEL: Record<MealType, string> = {
  morning: "아침",
  lunch: "점심",
  dinner: "저녁",
  total: "전체",
};

export type BudgetPlan = {
  meal_plan_id: number;
  monthly_budget: number;
  spent_amount: number;
  remaining: number;
  period_start: string;
  period_end: string;
  meal_type: MealType;
};

export type BudgetRankItem = {
  name?: string;
  label?: string;
  total: number;
  visits: number;
};

export type BudgetReport = {
  total_spent: number;
  saved_amount: number;
  top_restaurants: BudgetRankItem[];
  top_categories: BudgetRankItem[];
};

export async function fetchAllBudgetPlans(userId: number): Promise<BudgetPlan[]> {
  const res = await fetch("/api/gourmet/budget/plans", {
    headers: userHeader(userId),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`예산 조회 실패: ${res.status}`);
  return (await res.json()) as BudgetPlan[];
}

export async function fetchBudgetPlan(userId: number): Promise<BudgetPlan | null> {
  const res = await fetch("/api/gourmet/budget/plan", {
    headers: userHeader(userId),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`예산 조회 실패: ${res.status}`);
  return (await res.json()) as BudgetPlan | null;
}

export async function setBudget(
  userId: number,
  monthlyBudget: number,
  periodStart: string,
  periodEnd: string,
  mealType: MealType = "total",
): Promise<BudgetPlan> {
  const res = await fetch("/api/gourmet/budget/plan", {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...userHeader(userId) },
    body: JSON.stringify({
      monthly_budget: monthlyBudget,
      period_start: periodStart,
      period_end: periodEnd,
      meal_type: mealType,
    }),
  });
  if (!res.ok) throw new Error(`예산 설정 실패: ${res.status}`);
  return (await res.json()) as BudgetPlan;
}

export async function addExpense(
  userId: number,
  mealPlanId: number,
  amount: number,
  spentOn: string,
): Promise<BudgetPlan> {
  const res = await fetch("/api/gourmet/budget/expense", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...userHeader(userId) },
    body: JSON.stringify({
      meal_plan_id: mealPlanId,
      amount,
      spent_on: spentOn,
    }),
  });
  if (!res.ok) throw new Error(`지출 입력 실패: ${res.status}`);
  return (await res.json()) as BudgetPlan;
}

export async function fetchBudgetReport(
  userId: number,
  mealPlanId: number,
): Promise<BudgetReport> {
  const res = await fetch(`/api/gourmet/budget/report?meal_plan_id=${mealPlanId}`, {
    headers: userHeader(userId),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`리포트 조회 실패: ${res.status}`);
  return (await res.json()) as BudgetReport;
}

/** 이번 달 1일 ~ 말일 (YYYY-MM-DD). */
export function currentMonthPeriod(): { start: string; end: string } {
  const now = new Date();
  const fmt = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
      d.getDate(),
    ).padStart(2, "0")}`;
  return {
    start: fmt(new Date(now.getFullYear(), now.getMonth(), 1)),
    end: fmt(new Date(now.getFullYear(), now.getMonth() + 1, 0)),
  };
}

/** 기간 종료일까지 남은 일수로 나눈 하루 예산. */
export function dailyRemaining(plan: BudgetPlan): number {
  const end = new Date(plan.period_end);
  const today = new Date();
  const daysLeft = Math.max(
    1,
    Math.ceil((end.getTime() - today.getTime()) / 86_400_000) + 1,
  );
  return Math.floor(plan.remaining / daysLeft);
}
