"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home } from "lucide-react";
import { HOME_TOPIC_LINKS } from "@/lib/gourmet-topics";
import { CATEGORY_LINKS } from "@/lib/navigation";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useCategoryMenu } from "@/components/category-menu-context";

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-0.5 p-2" aria-label="음식 카테고리">
      <Link
        href="/"
        onClick={onNavigate}
        className={cn(
          "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition",
          pathname === "/"
            ? "bg-white/15 text-white"
            : "text-white/70 hover:bg-white/10 hover:text-white"
        )}
      >
        <Home className="h-5 w-5 shrink-0" aria-hidden />
        홈
      </Link>

      <p className="mb-1 mt-4 px-3 text-[10px] font-semibold uppercase tracking-wider text-white/40">
        카테고리
      </p>

      {CATEGORY_LINKS.map((cat) => {
        const active =
          pathname === cat.href || pathname.startsWith(`${cat.href}/`);
        return (
          <Link
            key={cat.slug}
            href={cat.href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition",
              active
                ? "bg-white/15 font-semibold text-white"
                : "text-white/70 hover:bg-white/10 hover:text-white"
            )}
          >
            <span className="text-lg leading-none" aria-hidden>
              {cat.block.emoji}
            </span>
            <span className="truncate">{cat.label}</span>
          </Link>
        );
      })}

      <p className="mb-1 mt-4 px-3 text-[10px] font-semibold uppercase tracking-wider text-white/40">
        주제별 추천
      </p>

      {HOME_TOPIC_LINKS.slice(0, 8).map((topic) => {
        const active =
          pathname === topic.href || pathname.startsWith(`${topic.href}/`);
        return (
          <Link
            key={topic.slug}
            href={topic.href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition",
              active
                ? "bg-white/15 font-semibold text-white"
                : "text-white/70 hover:bg-white/10 hover:text-white"
            )}
          >
            <span className="text-lg leading-none" aria-hidden>
              {topic.emoji}
            </span>
            <span className="truncate">{topic.title}</span>
          </Link>
        );
      })}
    </nav>
  );
}

/** 기본 숨김 — 열릴 때만 좌측에서 슬라이드 */
export default function CategorySidebarDrawer() {
  const { open, setOpen } = useCategoryMenu();

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetContent
        side="left"
        className="w-[min(280px,88vw)] border-white/10 bg-[#141414] p-0 text-white"
      >
        <SheetHeader className="border-b border-white/10 px-4 py-4 text-left">
          <SheetTitle className="text-white">GourmetMate 메뉴</SheetTitle>
        </SheetHeader>
        <NavLinks onNavigate={() => setOpen(false)} />
      </SheetContent>
    </Sheet>
  );
}
