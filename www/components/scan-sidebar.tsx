"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const NAV_ITEMS = [
  { href: "/", label: "홈", exact: true },
  { href: "/scan", label: "AI 스캐너", exact: true },
  { href: "/scan/report", label: "위험 진단 리포트" },
  { href: "/scan/guide", label: "비상 대응 가이드" },
  { href: "/scan/policy", label: "정부지원 대안 자금" },
  { href: "/scan/incident-report", label: "AI 경위서 작성", isNew: true },
];

function NavLinks({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-0.5 px-3 py-3">
      {NAV_ITEMS.map(({ href, label, exact, isNew }) => {
        const active = exact ? pathname === href : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onClose}
            className={cn(
              "flex items-center gap-[11px] rounded-[10px] px-3 py-2.5 text-[13.5px] font-medium transition-colors",
              active ? "text-slate-900" : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
            )}
          >
            <span
              className={cn(
                "h-[7px] w-[7px] shrink-0 rounded-[2px]",
                active ? "bg-indigo-600" : "bg-slate-300"
              )}
              aria-hidden
            />
            <span>{label}</span>
            {isNew && (
              <span className="ml-auto rounded-[5px] bg-indigo-50 px-1.5 py-0.5 text-[10px] font-bold text-indigo-600">
                NEW
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}

function SidebarBrand() {
  return (
    <div className="flex items-center gap-2.5 border-b border-slate-100 px-5 py-[18px]">
      <div className="flex h-8 w-8 items-center justify-center rounded-[9px] bg-indigo-600">
        <ShieldCheck className="h-4 w-4 text-white" aria-hidden />
      </div>
      <div>
        <div className="text-[15px] font-bold tracking-tight text-slate-900">SafeTeen Finance</div>
        <div className="mt-px text-[11px] text-slate-500">불법금융 실시간 진단</div>
      </div>
    </div>
  );
}

function SidebarFooter() {
  return (
    <div className="mt-auto border-t border-slate-100 px-5 py-4">
      <div className="text-[11.5px] leading-relaxed text-slate-500">
        긴급 상황이라면
        <br />
        <a href="tel:1332" className="font-bold text-indigo-600 hover:text-indigo-700">
          금융감독원 1332
        </a>{" "}
        로 바로 전화하세요.
      </div>
    </div>
  );
}

export function ScanSidebarDesktop() {
  return (
    <aside className="fixed bottom-0 left-0 top-[var(--site-header-height)] z-40 hidden w-56 flex-col border-r border-slate-200 bg-white md:flex">
      <SidebarBrand />
      <div className="flex-1 overflow-y-auto">
        <NavLinks />
      </div>
      <SidebarFooter />
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
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3.5">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4.5 w-4.5 text-indigo-600" aria-hidden />
            <span className="text-sm font-semibold text-slate-900">SafeTeen Finance</span>
          </div>
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
        <SidebarFooter />
      </aside>
    </>
  );
}
