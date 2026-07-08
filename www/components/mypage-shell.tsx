"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import MypageNav from "@/components/mypage-nav";
import { useAuth } from "@/components/auth-provider";

export default function MypageShell({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  const { user, ready } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (ready && !user) router.replace("/");
  }, [ready, user, router]);

  if (!ready) {
    return (
      <main className="mx-auto max-w-4xl px-4 pb-16 pt-[calc(var(--site-header-height)+2rem)]">
        <p className="text-sm text-[#6e6e73]">불러오는 중…</p>
      </main>
    );
  }

  if (!user) return null;

  return (
    <main className="mx-auto max-w-4xl px-4 pb-16 pt-[calc(var(--site-header-height)+2rem)]">
      <h1 className="mb-6 text-2xl font-semibold tracking-tight text-[#1d1d1f]">
        {title}
      </h1>
      <MypageNav />
      <div className="mt-8">{children}</div>
    </main>
  );
}
