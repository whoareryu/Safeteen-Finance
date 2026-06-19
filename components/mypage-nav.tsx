"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { isAdmin, useAuth } from "@/components/auth-provider";

const BASE_LINKS = [
  { href: "/mypage", label: "내 정보" },
  { href: "/mypage/favorites", label: "즐겨찾기" },
  { href: "/mypage/budget", label: "버짓설정" },
];

const ADMIN_LINKS = [
  { href: "/admin", label: "대시보드" },
  { href: "/mypage/customers", label: "고객관리" },
  { href: "/mypage/stores", label: "매점관리" },
];

export default function MypageNav() {
  const pathname = usePathname();
  const { user } = useAuth();
  const links = [...BASE_LINKS, ...(isAdmin(user) ? ADMIN_LINKS : [])];

  return (
    <nav
      className="flex flex-wrap gap-2 border-b border-black/10 pb-4"
      aria-label="마이페이지 메뉴"
    >
      {links.map((item) => {
        const active =
          pathname === item.href ||
          (item.href === "/mypage"
            ? pathname === "/mypage"
            : pathname.startsWith(item.href));
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "rounded-full px-4 py-2 text-sm transition",
              active
                ? "bg-[#1d1d1f] text-white"
                : "bg-black/[0.05] text-[#1d1d1f]/85 hover:bg-black/[0.08]"
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
