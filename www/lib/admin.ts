import type { UserRole } from "./auth";

export type AdminUser = {
  id: number;
  username: string;
  nickname: string;
  email: string;
  role: UserRole;
  region?: string | null;
  created_at: string;
  last_login_at: string | null;
};

export type AdminStats = {
  total_users: number;
  admin_count: number;
  new_today: number;
  new_this_week: number;
};

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: string };
    if (typeof body.detail === "string") return body.detail;
  } catch {
    /* ignore */
  }
  return "요청 처리에 실패했습니다.";
}

export async function fetchAdminStats(): Promise<AdminStats> {
  const res = await fetch("/api/auth/admin/stats");
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AdminStats;
}

export async function fetchAdminUsers(): Promise<AdminUser[]> {
  const res = await fetch("/api/auth/admin/users");
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AdminUser[];
}

export async function updateUserRole(userId: number, role: UserRole): Promise<AdminUser> {
  const res = await fetch(`/api/auth/admin/users/${userId}/role`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AdminUser;
}
