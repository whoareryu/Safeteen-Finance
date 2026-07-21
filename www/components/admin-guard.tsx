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
    if (!isAdmin(user)) router.replace("/mypage");
  }, [ready, user, router]);

  if (!ready || !user || !isAdmin(user)) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center p-4">
        <p className="text-sm text-muted-foreground">권한을 확인하는 중…</p>
      </div>
    );
  }

  return <>{children}</>;
}
