"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Dumbbell, Heart, Home, MessageCircle, User, Wallet } from "lucide-react";
import { cn } from "@/lib/utils";

const TABS = [
  { href: "/", label: "홈", Icon: Home },
  { href: "/couple-travel", label: "커플·여행", Icon: Heart },
  { href: "/health-diet", label: "헬스식단", Icon: Dumbbell },
  { href: "/budget", label: "버짓", Icon: Wallet },
  { href: "/social", label: "소셜", Icon: MessageCircle },
  { href: "/mypage", label: "마이", Icon: User },
] as const;

/** 하단 탭바 (기획서 3-4). 수업 영역(/portfolio)에선 숨김. */
export default function BottomTabBar() {
  const pathname = usePathname();
  if (pathname.startsWith("/portfolio")) return null;

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 flex border-t border-border bg-background/95 backdrop-blur">
      {TABS.map(({ href, label, Icon }) => {
        const active =
          href === "/" ? pathname === "/" : pathname.startsWith(href);
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
