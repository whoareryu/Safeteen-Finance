"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, User, X } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/admin", label: "대시보드", icon: LayoutDashboard, exact: true },
  { href: "/admin/users", label: "사용자 관리", icon: Users },
  { href: "/mypage", label: "내 정보", icon: User, exact: true },
];

function NavLinks({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1 px-2 py-4">
      {NAV_ITEMS.map(({ href, label, icon: Icon, exact }) => {
        const active = exact ? pathname === href : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onClose}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              active
                ? "bg-white/15 text-white"
                : "text-white/60 hover:bg-white/10 hover:text-white"
            )}
          >
            <Icon size={17} />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

export function AdminSidebarDesktop() {
  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-56 flex-col bg-[#1d1d1f] md:flex">
      <div className="flex h-14 items-center px-5">
        <span className="text-sm font-semibold tracking-wide text-white">Admin</span>
      </div>
      <div className="flex-1 overflow-y-auto">
        <NavLinks />
      </div>
    </aside>
  );
}

export function AdminSidebarMobile({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  if (!open) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/50 md:hidden"
        onClick={onClose}
        aria-hidden
      />
      <aside className="fixed inset-y-0 left-0 z-50 flex w-56 flex-col bg-[#1d1d1f] md:hidden">
        <div className="flex h-14 items-center justify-between px-5">
          <span className="text-sm font-semibold tracking-wide text-white">Admin</span>
          <button
            onClick={onClose}
            className="rounded p-1 text-white/60 hover:text-white"
            aria-label="메뉴 닫기"
          >
            <X size={18} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <NavLinks onClose={onClose} />
        </div>
      </aside>
    </>
  );
}
