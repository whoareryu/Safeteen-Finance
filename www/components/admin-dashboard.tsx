"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  TrendingUp,
  Heart,
  MessageCircle,
  UserPlus,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";

// ── Mock data ──────────────────────────────────────────────────────────────

const MONTHLY_DATA = [
  { month: "1월", visits: 1820, chats: 210 },
  { month: "2월", visits: 2340, chats: 280 },
  { month: "3월", visits: 2110, chats: 260 },
  { month: "4월", visits: 2780, chats: 340 },
  { month: "5월", visits: 3150, chats: 410 },
  { month: "6월", visits: 2940, chats: 380 },
  { month: "7월", visits: 3620, chats: 490 },
];

const CATEGORY_DATA = [
  { name: "한식", value: 38, color: "#ef4444" },
  { name: "카페·디저트", value: 24, color: "#f59e0b" },
  { name: "데이트", value: 18, color: "#8b5cf6" },
  { name: "가성비", value: 13, color: "#3b82f6" },
  { name: "기타", value: 7, color: "#10b981" },
];

const GOALS = [
  { label: "맛집 즐겨찾기", current: 7460, target: 10000, color: "#ef4444" },
  { label: "AI 채팅 이용", current: 3900, target: 5000, color: "#f97316" },
  { label: "월간 방문자", current: 36200, target: 40000, color: "#3b82f6" },
  { label: "신규 회원 가입", current: 850, target: 1000, color: "#10b981" },
];

const RECENT_USERS = [
  { nickname: "미식가_서울", restaurant: "광장시장 빈대떡", joined: "2025-07-18", status: "활성" },
  { nickname: "맛집탐험가", restaurant: "을지로 노포 국밥", joined: "2025-07-17", status: "활성" },
  { nickname: "foodie_kr", restaurant: "연남동 카페거리", joined: "2025-07-17", status: "활성" },
  { nickname: "점심뭐먹지", restaurant: "종로 순대국밥", joined: "2025-07-16", status: "활성" },
  { nickname: "서울맛집왕", restaurant: "홍대 양꼬치", joined: "2025-07-16", status: "휴면" },
  { nickname: "데이트코스", restaurant: "한남동 브런치", joined: "2025-07-15", status: "활성" },
  { nickname: "혼밥러버", restaurant: "을지로 돼지갈비", joined: "2025-07-15", status: "활성" },
];

const STATUS_STYLE: Record<string, string> = {
  활성: "bg-emerald-100 text-emerald-700",
  휴면: "bg-amber-100 text-amber-700",
};

// ── Sub-components ──────────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  sub,
  color,
  icon: Icon,
}: {
  label: string;
  value: string;
  sub: string;
  color: string;
  icon: React.ElementType;
}) {
  return (
    <div className="flex items-center gap-4 rounded-2xl bg-white p-4 shadow-sm dark:bg-[#111]">
      <div
        className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-white"
        style={{ backgroundColor: color }}
      >
        <Icon size={20} />
      </div>
      <div className="min-w-0">
        <p className="truncate text-xs text-[#6e6e73] dark:text-white/50">{label}</p>
        <p className="text-xl font-bold text-[#1d1d1f] dark:text-white">{value}</p>
        <p className="text-xs text-[#6e6e73] dark:text-white/50">{sub}</p>
      </div>
    </div>
  );
}

function SectionCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm dark:bg-[#111] md:p-5">
      <h3 className="mb-4 text-sm font-semibold text-[#1d1d1f] dark:text-white">{title}</h3>
      {children}
    </div>
  );
}

// ── Main component ──────────────────────────────────────────────────────────

export default function AdminDashboard() {
  return (
    <div className="space-y-4">
      <h1 className="text-lg font-bold text-[#1d1d1f] dark:text-white md:text-xl">대시보드</h1>

      {/* Stats cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="월간 방문자"
          value="36,200"
          sub="이번 달 페이지 방문"
          color="#3b82f6"
          icon={TrendingUp}
        />
        <StatCard
          label="맛집 즐겨찾기"
          value="7,460"
          sub="누적 즐겨찾기 수"
          color="#ef4444"
          icon={Heart}
        />
        <StatCard
          label="AI 채팅"
          value="3,900"
          sub="누적 Gemini 대화"
          color="#8b5cf6"
          icon={MessageCircle}
        />
        <StatCard
          label="신규 회원"
          value="850"
          sub="이번 달 가입"
          color="#f97316"
          icon={UserPlus}
        />
      </div>

      {/* Chart + Goals row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <SectionCard title="월간 현황">
          <div className="h-[200px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={MONTHLY_DATA} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: 8, fontSize: 12, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,0.12)" }}
                />
                <Line
                  type="monotone"
                  dataKey="visits"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  name="방문자 수"
                />
                <Line
                  type="monotone"
                  dataKey="chats"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={false}
                  name="AI 채팅"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 flex gap-4 text-xs text-[#6e6e73] dark:text-white/50">
            <span className="flex items-center gap-1"><span className="inline-block h-2 w-4 rounded bg-blue-500" /> 방문자 수</span>
            <span className="flex items-center gap-1"><span className="inline-block h-2 w-4 rounded bg-violet-500" /> AI 채팅</span>
          </div>
        </SectionCard>

        <div className="lg:col-span-2">
          <SectionCard title="목표 달성률">
            <div className="space-y-4">
              {GOALS.map((g) => {
                const pct = Math.round((g.current / g.target) * 100);
                return (
                  <div key={g.label}>
                    <div className="mb-1 flex items-center justify-between text-xs">
                      <span className="text-[#1d1d1f] dark:text-white">{g.label}</span>
                      <span className="font-medium" style={{ color: g.color }}>{pct}%</span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-[#f0f0f0] dark:bg-white/10">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{ width: `${pct}%`, backgroundColor: g.color }}
                      />
                    </div>
                    <p className="mt-0.5 text-right text-[10px] text-[#6e6e73] dark:text-white/40">
                      {g.current.toLocaleString()} / {g.target.toLocaleString()}
                    </p>
                  </div>
                );
              })}
            </div>
          </SectionCard>
        </div>
      </div>

      {/* Summary row */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {[
          { label: "등록 맛집 수", value: "2,840개", change: "+12%", up: true },
          { label: "활성 사용자", value: "1,240명", change: "+18%", up: true },
          { label: "AI 채팅 만족도", value: "94.2%", change: "+2.1%", up: true },
        ].map(({ label, value, change, up }) => (
          <div key={label} className="rounded-2xl bg-white p-4 shadow-sm dark:bg-[#111]">
            <p className="text-xs text-[#6e6e73] dark:text-white/50">{label}</p>
            <p className="mt-1 text-base font-bold text-[#1d1d1f] dark:text-white md:text-lg">{value}</p>
            <span
              className={`mt-1 inline-flex items-center gap-0.5 text-xs font-medium ${
                up ? "text-emerald-600" : "text-red-500"
              }`}
            >
              {up ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
              {change}
            </span>
          </div>
        ))}
      </div>

      {/* Category dist + Recent users */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <SectionCard title="카테고리별 검색 비율">
          <div className="flex flex-col items-center">
            <div className="h-[160px] w-full max-w-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={CATEGORY_DATA}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {CATEGORY_DATA.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ borderRadius: 8, fontSize: 12, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,0.12)" }}
                    formatter={(v: number) => [`${v}%`, ""]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 w-full space-y-2">
              {CATEGORY_DATA.map((d) => (
                <div key={d.name} className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-2">
                    <span
                      className="inline-block h-2.5 w-2.5 rounded-full"
                      style={{ backgroundColor: d.color }}
                    />
                    {d.name}
                  </span>
                  <span className="font-medium text-[#1d1d1f]">{d.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </SectionCard>

        <div className="lg:col-span-2">
          <SectionCard title="최근 가입 회원">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[360px] text-sm">
                <thead>
                  <tr className="border-b border-black/10 text-xs text-[#6e6e73] dark:border-white/10 dark:text-white/50">
                    <th className="pb-2 text-left font-medium">닉네임</th>
                    <th className="pb-2 text-left font-medium">첫 즐겨찾기</th>
                    <th className="pb-2 text-center font-medium">가입일</th>
                    <th className="pb-2 text-center font-medium">상태</th>
                  </tr>
                </thead>
                <tbody>
                  {RECENT_USERS.map((u) => (
                    <tr key={u.nickname} className="border-b border-black/5 last:border-0 dark:border-white/5">
                      <td className="py-2.5 font-medium text-[#1d1d1f] dark:text-white">{u.nickname}</td>
                      <td className="py-2.5 text-xs text-[#6e6e73] dark:text-white/50">{u.restaurant}</td>
                      <td className="py-2.5 text-center text-xs text-[#6e6e73] dark:text-white/50">{u.joined}</td>
                      <td className="py-2.5 text-center">
                        <span
                          className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                            STATUS_STYLE[u.status] ?? "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {u.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
