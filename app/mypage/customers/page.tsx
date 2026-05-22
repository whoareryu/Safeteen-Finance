"use client";

import { useEffect, useState } from "react";
import AdminGuard from "@/components/admin-guard";
import MypageShell from "@/components/mypage-shell";
import { useAuth } from "@/components/auth-provider";

type AdminUserRow = {
  id: number;
  username: string;
  nickname: string;
  email: string;
  role: string;
  created_at: string | null;
};

export default function CustomersAdminPage() {
  const { user } = useAuth();
  const [rows, setRows] = useState<AdminUserRow[]>([]);
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
          `/api/auth/admin/users?as_username=${encodeURIComponent(user.username)}`
        );
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(
            typeof body.detail === "string" ? body.detail : "목록을 불러오지 못했습니다."
          );
        }
        const data = (await res.json()) as AdminUserRow[];
        if (!cancelled) setRows(data);
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
    <MypageShell title="고객관리">
      <AdminGuard>
        {loading ? (
          <p className="text-sm text-[#6e6e73]">회원 목록을 불러오는 중…</p>
        ) : error ? (
          <p className="text-sm text-red-600">{error}</p>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-black/10 bg-white shadow-sm">
            <table className="w-full min-w-[32rem] text-left text-sm">
              <thead className="border-b border-black/10 bg-black/[0.03]">
                <tr>
                  <th className="px-4 py-3 font-medium">ID</th>
                  <th className="px-4 py-3 font-medium">아이디</th>
                  <th className="px-4 py-3 font-medium">닉네임</th>
                  <th className="px-4 py-3 font-medium">이메일</th>
                  <th className="px-4 py-3 font-medium">역할</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className="border-b border-black/5 last:border-0">
                    <td className="px-4 py-3">{r.id}</td>
                    <td className="px-4 py-3">{r.username}</td>
                    <td className="px-4 py-3">{r.nickname}</td>
                    <td className="px-4 py-3">{r.email}</td>
                    <td className="px-4 py-3">{r.role}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="px-4 py-3 text-xs text-[#6e6e73]">총 {rows.length}명</p>
          </div>
        )}
      </AdminGuard>
    </MypageShell>
  );
}
