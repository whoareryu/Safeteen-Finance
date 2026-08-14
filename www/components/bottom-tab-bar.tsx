"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, UserCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const TABS = [
  { href: "/", label: "홈", Icon: Home },
  { href: "/mypage", label: "마이페이지", Icon: UserCircle },
] as const;

export default function BottomTabBar() {
  const pathname = usePathname();

  // 접두사가 겹치는 탭 중, 가장 구체적으로(길게) 일치하는 탭 하나만 활성화한다.
  const activeHref = [...TABS]
    .sort((a, b) => b.href.length - a.href.length)
    .find((t) => (t.href === "/" ? pathname === "/" : pathname.startsWith(t.href)))?.href;

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 flex justify-center px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
      <div className="glass-panel flex items-center gap-1 rounded-full px-2 py-2">
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
