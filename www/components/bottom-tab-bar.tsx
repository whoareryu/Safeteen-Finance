"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CalendarCheck, Home, Leaf, MessageCircle, Sprout } from "lucide-react";
import { cn } from "@/lib/utils";

const TABS = [
  { href: "/", label: "홈", Icon: Home },
  { href: "/plant", label: "진단", Icon: Leaf },
  { href: "/plant/my-plants", label: "마이플랜트", Icon: Sprout },
  { href: "/plant/care-calendar", label: "케어일정", Icon: CalendarCheck },
  { href: "/social", label: "소셜", Icon: MessageCircle },
] as const;

/** 하단 탭바. 수업 영역(/portfolio)에선 숨김. */
export default function BottomTabBar() {
  const pathname = usePathname();
  if (pathname.startsWith("/portfolio")) return null;

  // "/plant"와 "/plant/my-plants"처럼 접두사가 겹치는 탭 중, 가장 구체적으로(길게) 일치하는 탭 하나만 활성화한다.
  const activeHref = [...TABS]
    .sort((a, b) => b.href.length - a.href.length)
    .find((t) => (t.href === "/" ? pathname === "/" : pathname.startsWith(t.href)))?.href;

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 flex border-t border-border bg-background/95 backdrop-blur">
      {TABS.map(({ href, label, Icon }) => {
        const active = href === activeHref;
        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px]",
              active ? "text-primary" : "text-muted-foreground",
            )}
          >
            <Icon className="h-5 w-5" aria-hidden />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
