"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";

import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

const ITEMS = [
  { href: "/portfolio/titanic/data-collection", label: "1. 데이터 수집" },
  { href: "/portfolio/titanic/data-analysis", label: "2. 데이터 분석" },
  { href: "/portfolio/titanic/data-modeling", label: "3. 데이터 모델링" },
  { href: "/portfolio/titanic/passenger-list", label: "4. 승객 명단" },
] as const;

export default function LessonMobileDrawer() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const currentLabel = useMemo(() => {
    const hit = ITEMS.find((it) => pathname === it.href || pathname.startsWith(`${it.href}/`));
    return hit?.label ?? "메뉴";
  }, [pathname]);

  return (
    <div className="md:hidden">
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-md px-2 py-1 text-xs font-medium text-[#1d1d1f]/85 hover:bg-black/[0.04]"
            aria-label="LESSON 메뉴 열기"
          >
            <Menu className="h-4 w-4" aria-hidden />
            {currentLabel}
          </button>
        </SheetTrigger>
        <SheetContent side="left" className="bg-[#fbfbfd] p-0">
          <SheetHeader className="border-b border-black/[0.06]">
            <SheetTitle className="text-sm tracking-[0.18em]">LESSON</SheetTitle>
          </SheetHeader>

          <div className="p-4">
            <p className="mb-2 text-xs font-semibold tracking-[0.18em] text-[#6e6e73]">
              타이타닉
            </p>
            <nav className="space-y-1">
              {ITEMS.map((it) => {
                const active = pathname === it.href || pathname.startsWith(`${it.href}/`);
                return (
                  <Link
                    key={it.href}
                    href={it.href}
                    onClick={() => setOpen(false)}
                    className={cn(
                      "block rounded-md px-2 py-2 text-sm text-[#1d1d1f]/80 hover:bg-black/[0.04]",
                      active && "bg-black/[0.06] font-medium text-[#1d1d1f]"
                    )}
                  >
                    {it.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}

