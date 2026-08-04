"use client";

import { useEffect, useState } from "react";
import { Users, ShieldCheck, UserPlus, CalendarDays } from "lucide-react";
import { fetchAdminStats, type AdminStats } from "@/lib/admin";
import { Card } from "@/components/ui/card";

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: number | string;
}) {
  return (
    <Card className="flex-row items-center gap-4 p-5">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Icon size={18} />
      </div>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </Card>
  );
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAdminStats()
      .then(setStats)
      .catch((e) => setError(e instanceof Error ? e.message : "통계를 불러오지 못했습니다."));
  }, []);

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="mb-6 text-2xl font-bold">대시보드</h1>

      {error ? <p className="text-sm text-destructive">{error}</p> : null}

      {stats ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard icon={Users} label="전체 사용자" value={stats.total_users} />
          <StatCard icon={ShieldCheck} label="관리자 수" value={stats.admin_count} />
          <StatCard icon={UserPlus} label="오늘 가입" value={stats.new_today} />
          <StatCard icon={CalendarDays} label="이번 주 가입" value={stats.new_this_week} />
        </div>
      ) : !error ? (
        <p className="text-sm text-muted-foreground">불러오는 중…</p>
      ) : null}
    </div>
  );
}
