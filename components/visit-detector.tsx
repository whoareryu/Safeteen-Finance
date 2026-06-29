"use client";

import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/auth-provider";
import { addExpense, fetchBudgetPlan } from "@/lib/gourmet-budget";
import {
  confirmVisit,
  distanceMeters,
  getVisitTarget,
  type VisitTarget,
} from "@/lib/gourmet-visit";
import { cn } from "@/lib/utils";

const RADIUS_M = 200;

/**
 * 추천 식당 반경 200m 진입 감지 → 방문 확인 팝업 (기획서 4-2).
 * 웹 한계: 앱이 열려 있을 때만 위치 감지(백그라운드 X). 수업(/portfolio) 제외.
 */
export default function VisitDetector() {
  const { user, ready } = useAuth();
  const pathname = usePathname();
  const excluded = pathname.startsWith("/portfolio");

  const [target, setTarget] = useState<VisitTarget | null>(null);
  const [rating, setRating] = useState(0);
  const [amount, setAmount] = useState("");
  const [done, setDone] = useState(false);
  const promptedRef = useRef<number | null>(null);

  useEffect(() => {
    if (!ready || !user || excluded) return;
    if (typeof navigator === "undefined" || !navigator.geolocation) return;
    const t = getVisitTarget();
    if (!t || !t.latitude || !t.longitude) return;

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const d = distanceMeters(
          pos.coords.latitude,
          pos.coords.longitude,
          t.latitude,
          t.longitude,
        );
        if (d <= RADIUS_M && promptedRef.current !== t.id) {
          promptedRef.current = t.id;
          setRating(0);
          setAmount("");
          setDone(false);
          setTarget(t);
        }
      },
      () => {},
      { enableHighAccuracy: true, maximumAge: 30_000 },
    );
    return () => navigator.geolocation.clearWatch(watchId);
  }, [ready, user, excluded]);

  if (!target || excluded) return null;

  const submit = async () => {
    if (!user) return;
    try {
      await confirmVisit(user.id, {
        restaurant_id: target.id,
        rating: rating || null,
        latitude: target.latitude,
        longitude: target.longitude,
      });
      if (amount) {
        const plan = await fetchBudgetPlan(user.id);
        if (plan) {
          await addExpense(
            user.id,
            plan.meal_plan_id,
            Number(amount),
            new Date().toISOString().slice(0, 10),
          );
        }
      }
      setDone(true);
      setTimeout(() => setTarget(null), 1500);
    } catch {
      /* 저장 실패 시 팝업 유지 */
    }
  };

  return (
    <div className="fixed inset-x-4 bottom-24 z-[60] mx-auto max-w-sm rounded-2xl bg-card p-5 shadow-2xl ring-1 ring-border">
      {done ? (
        <p className="text-center text-sm font-semibold text-primary">
          평가 감사합니다! 🙏
        </p>
      ) : (
        <>
          <p className="text-sm">
            혹시 <b>{target.name}</b> 방문하셨나요?
          </p>
          <div className="mt-3 flex justify-center gap-1">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                type="button"
                aria-label={`${n}점`}
                onClick={() => setRating(n)}
                className={cn("text-2xl", n <= rating ? "opacity-100" : "opacity-30")}
              >
                ⭐
              </button>
            ))}
          </div>
          <input
            type="number"
            inputMode="numeric"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="얼마 쓰셨나요? (선택)"
            className="mt-3 w-full rounded-xl border border-border px-3 py-2 text-sm"
          />
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={() => setTarget(null)}
              className="flex-1 rounded-xl bg-muted py-2 text-sm font-semibold text-muted-foreground"
            >
              아니요
            </button>
            <button
              type="button"
              onClick={() => void submit()}
              className="flex-1 rounded-xl bg-primary py-2 text-sm font-semibold text-white"
            >
              평가 남기기
            </button>
          </div>
        </>
      )}
    </div>
  );
}
