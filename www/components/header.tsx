"use client";

import { useState } from "react";
import { LogIn, LogOut, ShieldCheck, UserCircle } from "lucide-react";
import { ThemeToggle } from "./theme-toggle";
import Link from "next/link";
import { usePathname } from "next/navigation";
import AuthModal from "./auth-modal";
import WeatherWidget from "./weather-widget";
import { isAdmin, useAuth } from "./auth-provider";
import { cn } from "@/lib/utils";

export default function Header() {
  const pathname = usePathname();
  const { user, ready, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const showWeather = pathname === "/";

  const openLogin = () => setShowAuthModal(true);

  const isPortfolioActive =
    pathname === "/portfolio" || pathname.startsWith("/portfolio/");

  const isMypageActive = pathname.startsWith("/plant/care-calendar");

  return (
    <>
      <header className="site-header--apple fixed top-0 left-0 right-0 z-50 w-full">
        <div className="relative flex h-14 w-full items-center px-4 sm:px-6 lg:px-8 md:h-[3.25rem]">
          <div className="flex shrink-0 items-center gap-2 md:gap-3">
            <Link
              href="/"
              className="shrink-0 text-lg font-semibold tracking-tight text-[#1d1d1f] hover:opacity-80 md:text-xl"
            >
              새싹
            </Link>
          </div>

          <nav
            className="pointer-events-none absolute left-1/2 hidden -translate-x-1/2 md:block"
            aria-label="주요 메뉴"
          >
            <Link
              href="/portfolio/titanic"
              className={cn(
                "pointer-events-auto apple-nav-link inline-flex items-center rounded-md px-3 py-1.5 text-sm font-normal text-[#1d1d1f]/85 transition hover:bg-black/[0.04]",
                isPortfolioActive && "bg-black/[0.06] font-medium text-[#1d1d1f]"
              )}
            >
              LESSON
            </Link>
          </nav>

          <div className="ml-auto flex min-w-0 items-center justify-end gap-2 overflow-x-auto py-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden md:gap-3">
            <Link
              href="/portfolio/titanic"
              className={cn(
                "shrink-0 rounded-md px-2 py-1 text-xs text-[#1d1d1f]/85 md:hidden",
                isPortfolioActive && "font-medium text-[#1d1d1f]"
              )}
            >
              LESSON
            </Link>

            {showWeather ? (
              <div className="hidden shrink-0 sm:block">
                <WeatherWidget />
              </div>
            ) : null}

            <div className="shrink-0">
              <ThemeToggle />
            </div>

            {ready && user ? (
              <>
                <Link
                  href="/mypage"
                  className="hidden max-w-[120px] shrink-0 truncate text-xs text-[#6e6e73] hover:underline md:inline lg:max-w-none lg:text-sm"
                >
                  {user.nickname}님
                </Link>
                <Link
                  href="/plant/care-calendar"
                  aria-label="내 식물"
                  className={cn(
                    "apple-nav-link inline-flex shrink-0 items-center gap-1 rounded-full border border-black/10 bg-white px-2 py-1.5 text-xs text-[#1d1d1f]/85 shadow-sm transition hover:bg-black/[0.04] sm:px-3 md:text-sm",
                    isMypageActive && "border-black/20 bg-black/[0.06] font-medium text-[#1d1d1f]"
                  )}
                >
                  <UserCircle className="h-3.5 w-3.5" aria-hidden />
                  <span className="hidden sm:inline">내 식물</span>
                </Link>
                {isAdmin(user) ? (
                  <Link
                    href="/admin"
                    aria-label="관리자"
                    className={cn(
                      "apple-nav-link inline-flex shrink-0 items-center gap-1 rounded-full border border-black/10 bg-white px-2 py-1.5 text-xs text-[#1d1d1f]/85 shadow-sm transition hover:bg-black/[0.04] sm:px-3 md:text-sm",
                      pathname.startsWith("/admin") && "border-black/20 bg-black/[0.06] font-medium text-[#1d1d1f]"
                    )}
                  >
                    <ShieldCheck className="h-3.5 w-3.5" aria-hidden />
                    <span className="hidden sm:inline">관리자</span>
                  </Link>
                ) : null}
                <button
                  type="button"
                  onClick={logout}
                  aria-label="로그아웃"
                  className="apple-nav-cta flex shrink-0 items-center gap-1.5 rounded-full px-2 py-1.5 text-xs sm:px-3 md:text-sm"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">로그아웃</span>
                </button>
              </>
            ) : (
              <button
                type="button"
                onClick={openLogin}
                className="apple-nav-cta flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-xs md:text-sm"
              >
                <LogIn className="h-3.5 w-3.5" />
                로그인
              </button>
            )}
          </div>
        </div>

      </header>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </>
  );
}
