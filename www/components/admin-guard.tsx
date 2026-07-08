"use client";

// TODO: 운영 배포 전 아래 주석을 해제하고 bypass 라인을 제거할 것
// import { useEffect } from "react";
// import { useRouter } from "next/navigation";
// import { isAdmin, useAuth } from "@/components/auth-provider";

export default function AdminGuard({ children }: { children: React.ReactNode }) {
  // 개발·데모용 임시 bypass — 인증 없이 어드민 접근 허용
  return <>{children}</>;

  // ── 운영 코드 (복원 시 위 return 제거) ──────────────────────────
  // const { user, ready } = useAuth();
  // const router = useRouter();
  //
  // useEffect(() => {
  //   if (!ready) return;
  //   if (!user) { router.replace("/"); return; }
  //   if (!isAdmin(user)) router.replace("/mypage");
  // }, [ready, user, router]);
  //
  // if (!ready || !user || !isAdmin(user)) {
  //   return <p className="text-sm text-[#6e6e73]">권한을 확인하는 중…</p>;
  // }
  // return <>{children}</>;
}
