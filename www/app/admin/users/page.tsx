"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { fetchAdminUsers, updateUserRole, type AdminUser } from "@/lib/admin";
import type { UserRole } from "@/lib/auth";

const ROLE_OPTIONS: UserRole[] = ["admin", "user", "partner"];

export default function AdminUsersPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  useEffect(() => {
    load();
  }, []);

  function load() {
    setLoading(true);
    fetchAdminUsers()
      .then(setUsers)
      .catch((e) => setError(e instanceof Error ? e.message : "사용자 목록을 불러오지 못했습니다."))
      .finally(() => setLoading(false));
  }

  async function handleRoleChange(userId: number, role: UserRole) {
    setUpdatingId(userId);
    setError(null);
    try {
      const updated = await updateUserRole(userId, role);
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "권한 변경에 실패했습니다.");
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="mb-6 text-2xl font-bold">사용자 관리</h1>

      {error ? <p className="mb-4 text-sm text-destructive">{error}</p> : null}

      {loading ? (
        <p className="text-sm text-muted-foreground">불러오는 중…</p>
      ) : (
        <div className="card-light overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-border text-xs text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">닉네임</th>
                <th className="px-4 py-3 font-medium">이메일</th>
                <th className="px-4 py-3 font-medium">가입일</th>
                <th className="px-4 py-3 font-medium">권한</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-border last:border-0">
                  <td className="px-4 py-3">{u.nickname}</td>
                  <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {new Date(u.created_at).toLocaleDateString("ko-KR")}
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={u.role}
                      disabled={updatingId === u.id || (u.id === currentUser?.id && u.role === "admin")}
                      onChange={(e) => handleRoleChange(u.id, e.target.value as UserRole)}
                      className="input-light w-28 py-1.5 text-xs disabled:opacity-50"
                    >
                      {ROLE_OPTIONS.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
