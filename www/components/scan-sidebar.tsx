"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AlertTriangle, FileText, HeartPulse, ScanSearch, ShieldCheck, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const NAV_ITEMS = [
  { href: "/scan", label: "AI 스캐너", icon: ScanSearch, exact: true },
  { href: "/scan/report", label: "위험 진단 리포트", icon: AlertTriangle },
  { href: "/scan/policy", label: "정부지원 대안 자금", icon: FileText },
  { href: "/scan/guide", label: "비상 대응 가이드", icon: HeartPulse },
];

function NavLinks({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1 px-3 py-4">
      {NAV_ITEMS.map(({ href, label, icon: Icon, exact }) => {
        const active = exact ? pathname === href : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onClose}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              active ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            )}
          >
            <Icon size={17} aria-hidden />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

export function ScanSidebarDesktop() {
  return (
    <aside className="fixed bottom-0 left-0 top-[var(--site-header-height)] z-40 hidden w-56 flex-col border-r border-slate-200 bg-white md:flex">
      <div className="flex h-16 items-center gap-2 px-4">
        <ShieldCheck className="h-5 w-5 text-indigo-600" aria-hidden />
        <span className="text-sm font-semibold text-slate-900">FinShield Youth</span>
      </div>
      <div className="flex-1 overflow-y-auto">
        <NavLinks />
      </div>
    </aside>
  );
}

export function ScanSidebarMobile({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;

  return (
    <>
      <div
        className="fixed bottom-0 left-0 right-0 top-[var(--site-header-height)] z-40 bg-black/40 md:hidden"
        onClick={onClose}
        aria-hidden
      />
      <aside className="fixed bottom-0 left-0 top-[var(--site-header-height)] z-40 flex w-64 flex-col bg-white md:hidden">
        <div className="flex h-14 items-center justify-between px-4">
          <span className="text-sm font-semibold text-slate-900">FinShield Youth</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-auto w-auto rounded p-1 text-slate-400 hover:bg-transparent hover:text-slate-700"
            aria-label="메뉴 닫기"
          >
            <X size={18} />
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <NavLinks onClose={onClose} />
        </div>
      </aside>
    </>
  );
}
