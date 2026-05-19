"use client";

import { useState } from "react";
import { ChevronDown, LogIn, LogOut } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import AuthModal from "./auth-modal";
import WeatherWidget from "./weather-widget";
import { useAuth } from "./auth-provider";
import { CATEGORY_LINKS } from "@/lib/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

export default function Header() {
  const pathname = usePathname();
  const { user, ready, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authView, setAuthView] = useState<"login" | "signup">("login");
  const showWeather = pathname === "/";

  const openLogin = () => {
    setAuthView("login");
    setShowAuthModal(true);
  };

  const isPortfolioActive =
    pathname === "/portfolio" || pathname.startsWith("/portfolio/");

  return (
    <>
      <header className="site-header--apple fixed top-0 left-0 right-0 z-50">
        <div className="mx-auto flex h-[var(--site-header-height)] max-w-[1200px] items-center justify-between gap-4 px-4 md:px-6">
          <Link
            href="/"
            className="shrink-0 text-lg font-semibold tracking-tight text-[#1d1d1f] hover:opacity-80 md:text-xl"
          >
            GourmetMate
          </Link>

          <nav
            className="hidden flex-1 items-center justify-center gap-0.5 md:flex"
            aria-label="주요 카테고리"
          >
            {CATEGORY_LINKS.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "apple-nav-link shrink-0 rounded-md px-2 py-1.5 text-[11px] font-normal text-[#1d1d1f]/85 transition hover:bg-black/[0.04] hover:text-[#1d1d1f] lg:px-2.5 lg:text-xs xl:text-sm",
                    active && "bg-black/[0.06] font-medium text-[#1d1d1f]"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}

            <DropdownMenu>
              <DropdownMenuTrigger
                className={cn(
                  "apple-nav-link inline-flex items-center gap-0.5 rounded-md px-2.5 py-1.5 text-xs font-normal text-[#1d1d1f]/85 outline-none transition hover:bg-black/[0.04] lg:px-3 lg:text-sm",
                  isPortfolioActive && "bg-black/[0.06] font-medium text-[#1d1d1f]"
                )}
              >
                Portfolio
                <ChevronDown className="h-3.5 w-3.5 opacity-60" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="center" className="min-w-[10rem]">
                <DropdownMenuItem asChild>
                  <Link href="/portfolio">전체 보기</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/portfolio/seoulmate">SeoulMate</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/portfolio/titanic">타이타닉</Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </nav>

          <div className="flex shrink-0 items-center gap-2 md:gap-3">
            {showWeather ? (
              <div className="hidden sm:block">
                <WeatherWidget />
              </div>
            ) : null}

            {ready && user ? (
              <>
                <span className="hidden max-w-[120px] truncate text-xs text-[#6e6e73] md:inline lg:max-w-none lg:text-sm">
                  {user.nickname}님
                </span>
                <button
                  type="button"
                  onClick={logout}
                  className="apple-nav-cta flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs md:text-sm"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  로그아웃
                </button>
              </>
            ) : (
              <button
                type="button"
                onClick={openLogin}
                className="apple-nav-cta flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs md:text-sm"
              >
                <LogIn className="h-3.5 w-3.5" />
                로그인
              </button>
            )}
          </div>
        </div>

        {/* 모바일 카테고리 스크롤 */}
        <nav
          className="flex gap-1 overflow-x-auto border-t border-black/[0.06] px-3 py-2 md:hidden"
          aria-label="모바일 카테고리"
        >
          {CATEGORY_LINKS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "shrink-0 rounded-full px-3 py-1 text-xs text-[#1d1d1f]/85",
                (pathname === item.href ||
                  pathname.startsWith(`${item.href}/`)) &&
                  "bg-[#1d1d1f] text-white"
              )}
            >
              {item.label}
            </Link>
          ))}
          <Link
            href="/portfolio"
            className={cn(
              "shrink-0 rounded-full px-3 py-1 text-xs text-[#1d1d1f]/85",
              isPortfolioActive && "bg-[#1d1d1f] text-white"
            )}
          >
            Portfolio
          </Link>
        </nav>
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialView={authView}
      />
    </>
  );
}
