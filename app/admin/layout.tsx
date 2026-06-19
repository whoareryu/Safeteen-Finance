"use client";

import { useState } from "react";
import { Menu } from "lucide-react";
import AdminGuard from "@/components/admin-guard";
import {
  AdminSidebarDesktop,
  AdminSidebarMobile,
} from "@/components/admin-sidebar";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <AdminGuard>
      <AdminSidebarDesktop />
      <AdminSidebarMobile
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="min-h-screen bg-[#f5f5f7] dark:bg-[#0a0a0a] md:pl-56">
        {/* Mobile header — site header 높이만큼 내려서 겹치지 않게 */}
        <header className="sticky top-[var(--site-header-height)] z-30 flex h-14 items-center gap-3 border-b border-black/10 bg-white px-4 dark:border-white/10 dark:bg-[#111] md:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="rounded-lg p-1.5 text-[#1d1d1f]/60 hover:bg-black/5 dark:text-white/60 dark:hover:bg-white/10"
            aria-label="메뉴 열기"
          >
            <Menu size={20} />
          </button>
          <span className="text-sm font-semibold text-[#1d1d1f] dark:text-white">Admin</span>
        </header>

        <main className="p-4 md:p-6">{children}</main>
      </div>
    </AdminGuard>
  );
}
