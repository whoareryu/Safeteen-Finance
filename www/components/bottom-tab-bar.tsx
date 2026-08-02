"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  CalendarCheck,
  Home,
  Leaf,
  Sprout,
  UserCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

const TABS = [
  { href: "/", label: "홈", Icon: Home },
  { href: "/plant", label: "진단", Icon: Leaf },
  { href: "/plant/my-plants", label: "마이플랜트", Icon: Sprout },
  { href: "/plant/care-calendar", label: "케어일정", Icon: CalendarCheck },
  { href: "/mypage", label: "마이페이지", Icon: UserCircle },
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
    <nav className="fixed inset-x-0 bottom-0 z-40 flex justify-center px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
      <div className="saessak-glass-panel flex items-center gap-1 rounded-full px-2 py-2">
        {TABS.map(({ href, label, Icon }) => {
          const active = href === activeHref;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex flex-col items-center gap-0.5 rounded-full px-3.5 py-1.5 text-[10px] font-medium transition-colors",
                active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground",
              )}
            >
              <Icon className="h-5 w-5" aria-hidden />
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
