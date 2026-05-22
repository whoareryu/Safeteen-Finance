"use client";

import { useEffect, useState } from "react";
import AdminGuard from "@/components/admin-guard";
import MypageShell from "@/components/mypage-shell";
import { useAuth } from "@/components/auth-provider";

type StoreSummary = {
  restaurants_count: number;
  sample: Array<{
    id: number;
    name: string;
    category_label: string;
    district: string;
    biz_number: string;
  }>;
};

export default function StoresAdminPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<StoreSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.username) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `/api/gourmet/admin/stores/summary?as_username=${encodeURIComponent(user.username)}`
        );
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(
            typeof body.detail === "string" ? body.detail : "집계를 불러오지 못했습니다."
          );
        }
        const data = (await res.json()) as StoreSummary;
        if (!cancelled) setSummary(data);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "오류");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user?.username]);

  return (
    <MypageShell title="매점관리">
      <AdminGuard>
        {loading ? (
          <p className="text-sm text-[#6e6e73]">매장 정보를 불러오는 중…</p>
        ) : error ? (
          <p className="text-sm text-red-600">{error}</p>
        ) : summary ? (
          <div className="space-y-6">
            <div className="rounded-2xl border border-black/10 bg-white p-5 shadow-sm">
              <p className="text-sm text-[#6e6e73]">등록 매장 (restaurants)</p>
              <p className="mt-1 text-2xl font-semibold">
                {summary.restaurants_count.toLocaleString()}
              </p>
            </div>
            <div className="overflow-x-auto rounded-2xl border border-black/10 bg-white shadow-sm">
              <p className="border-b border-black/10 px-4 py-3 text-sm font-medium">
                샘플 매장 (최대 20건)
              </p>
              <table className="w-full min-w-[28rem] text-left text-sm">
                <thead className="border-b border-black/10 bg-black/[0.03]">
                  <tr>
                    <th className="px-4 py-3 font-medium">ID</th>
                    <th className="px-4 py-3 font-medium">상호</th>
                    <th className="px-4 py-3 font-medium">카테고리</th>
                    <th className="px-4 py-3 font-medium">지역</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.sample.map((r) => (
                    <tr key={r.id} className="border-b border-black/5 last:border-0">
                      <td className="px-4 py-3">{r.id}</td>
                      <td className="px-4 py-3">{r.name}</td>
                      <td className="px-4 py-3">{r.category_label}</td>
                      <td className="px-4 py-3">{r.district}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}
      </AdminGuard>
    </MypageShell>
  );
}
