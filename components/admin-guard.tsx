"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAdmin, useAuth } from "@/components/auth-provider";

export default function AdminGuard({ children }: { children: React.ReactNode }) {
  const { user, ready } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!ready) return;
    if (!user) {
      router.replace("/");
      return;
    }
    if (!isAdmin(user)) {
      router.replace("/mypage");
    }
  }, [ready, user, router]);

  if (!ready || !user || !isAdmin(user)) {
    return (
      <p className="text-sm text-[#6e6e73]">권한을 확인하는 중…</p>
    );
  }

  return <>{children}</>;
}
