"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/components/auth-provider";
import { fetchMyPreference } from "@/lib/gourmet-onboarding";

/**
 * 첫 가입(온보딩 미완료) 사용자를 /onboarding 으로 유도.
 * 수업 영역(/portfolio)과 온보딩 페이지 자체는 제외.
 */
export default function OnboardingGate() {
  const { user, ready } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!ready || !user) return;
    if (pathname.startsWith("/onboarding") || pathname.startsWith("/portfolio")) {
      return;
    }
    let cancelled = false;
    fetchMyPreference(user.id)
      .then((pref) => {
        if (!cancelled && !pref.completed) router.replace("/onboarding");
      })
      .catch(() => {
        /* 온보딩 조회 실패 시 유도하지 않음 */
      });
    return () => {
      cancelled = true;
    };
  }, [ready, user, pathname, router]);

  return null;
}
