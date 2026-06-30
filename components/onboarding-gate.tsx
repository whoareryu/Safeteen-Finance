"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/components/auth-provider";
import {
  fetchMyPreference,
  isOnboardingLocallyDone,
  markOnboardingDone,
} from "@/lib/gourmet-onboarding";

const SKIP_PATHS = ["/onboarding", "/portfolio"];

export default function OnboardingGate() {
  const { user, ready } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!ready || !user) return;
    if (SKIP_PATHS.some((p) => pathname.startsWith(p))) return;

    // localStorage 캐시 우선 — 완료된 사용자는 API 호출 없이 통과
    if (isOnboardingLocallyDone(user.id)) return;

    let cancelled = false;
    fetchMyPreference(user.id)
      .then((pref) => {
        if (cancelled) return;
        if (pref.completed) {
          markOnboardingDone(user.id);
        } else {
          router.replace("/onboarding");
        }
      })
      .catch(() => {
        // 네트워크·서버 오류 시 온보딩으로 보내지 않음 (오탐 방지)
      });

    return () => {
      cancelled = true;
    };
  }, [ready, user, pathname, router]);

  return null;
}
