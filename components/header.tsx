"use client";

import { useEffect, useState } from "react";
import { ChevronDown, LogIn, LogOut, Menu, UserCircle } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import AuthModal from "./auth-modal";
import WeatherWidget from "./weather-widget";
import { isAdmin, useAuth } from "./auth-provider";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useCategoryMenu } from "@/components/category-menu-context";
import LessonMobileDrawer from "@/components/lesson-mobile-drawer";

function CategoryMenuButton() {
  const { setOpen } = useCategoryMenu();
  return (
    <button
      type="button"
      onClick={() => setOpen(true)}
      className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-sm text-[#1d1d1f]/85 transition hover:bg-black/[0.06]"
      aria-label="카테고리 메뉴 열기"
    >
      <Menu className="h-5 w-5" aria-hidden />
      <span className="hidden sm:inline">메뉴</span>
    </button>
  );
}

export default function Header() {
  const pathname = usePathname();
  const { user, ready, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authView, setAuthView] = useState<"login" | "signup">("login");
  const showWeather = pathname === "/";
  const isLessonActive = pathname.startsWith("/portfolio/titanic");

  const openLogin = () => {
    setAuthView("login");
    setShowAuthModal(true);
  };

  const isPortfolioActive =
    pathname === "/portfolio" || pathname.startsWith("/portfolio/");

  const showCategoryMenu =
    pathname === "/" ||
    pathname.startsWith("/food/") ||
    pathname.startsWith("/topics/") ||
    pathname.startsWith("/restaurants/");

  const isMypageActive = pathname.startsWith("/mypage");

  useEffect(() => {
    const el = document.documentElement;
    if (isLessonActive) el.classList.add("has-lesson-subbar");
    else el.classList.remove("has-lesson-subbar");
    return () => el.classList.remove("has-lesson-subbar");
  }, [isLessonActive]);

  return (
    <>
      <header className="site-header--apple fixed top-0 left-0 right-0 z-50 w-full">
        <div className="relative flex h-14 w-full items-center px-4 sm:px-6 lg:px-8 md:h-[3.25rem]">
          <div className="flex shrink-0 items-center gap-2 md:gap-3">
            {showCategoryMenu ? <CategoryMenuButton /> : null}
            <Link
              href="/"
              className="shrink-0 text-lg font-semibold tracking-tight text-[#1d1d1f] hover:opacity-80 md:text-xl"
            >
              GourmetMate
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

          <div className="ml-auto flex shrink-0 items-center justify-end gap-2 md:gap-3">
            <Link
              href="/portfolio/titanic"
              className={cn(
                "rounded-md px-2 py-1 text-xs text-[#1d1d1f]/85 md:hidden",
                isPortfolioActive && "font-medium text-[#1d1d1f]"
              )}
            >
              LESSON
            </Link>

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
                {isAdmin(user) ? (
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      className={cn(
                        "apple-nav-link inline-flex items-center gap-1 rounded-full border border-black/10 bg-white px-3 py-1.5 text-xs text-[#1d1d1f]/85 shadow-sm transition hover:bg-black/[0.04] md:text-sm",
                        isMypageActive && "border-black/20 bg-black/[0.06] font-medium text-[#1d1d1f]"
                      )}
                    >
                      <UserCircle className="h-3.5 w-3.5" aria-hidden />
                      마이페이지
                      <ChevronDown className="h-3 w-3 opacity-60" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="min-w-[11rem]">
                      <DropdownMenuItem asChild>
                        <Link href="/mypage">내 정보</Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href="/mypage/favorites">즐겨찾기</Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href="/mypage/budget">버짓설정</Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href="/mypage/customers">고객관리</Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href="/mypage/stores">매점관리</Link>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                ) : (
                  <Link
                    href="/mypage"
                    className={cn(
                      "apple-nav-link inline-flex items-center gap-1 rounded-full border border-black/10 bg-white px-3 py-1.5 text-xs text-[#1d1d1f]/85 shadow-sm transition hover:bg-black/[0.04] md:text-sm",
                      isMypageActive && "border-black/20 bg-black/[0.06] font-medium text-[#1d1d1f]"
                    )}
                  >
                    <UserCircle className="h-3.5 w-3.5" aria-hidden />
                    마이페이지
                  </Link>
                )}
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

        {isLessonActive ? (
          <div className="border-t border-black/[0.06] bg-[#fbfbfd]/80 backdrop-blur">
            <div className="mx-auto flex h-10 max-w-6xl items-center gap-2 px-4 sm:px-6 lg:px-8">
              <LessonMobileDrawer />

              <span className="hidden text-xs font-semibold tracking-[0.18em] text-[#6e6e73] md:inline">
                TITANIC
              </span>
              <div className="hidden h-4 w-px bg-black/[0.12] md:block" />
              <Link
                href="/portfolio/titanic/data-collection"
                className={cn(
                  "hidden rounded-md px-2 py-1 text-xs text-[#1d1d1f]/80 hover:bg-black/[0.04] md:inline-flex",
                  pathname.startsWith("/portfolio/titanic/data-collection") &&
                    "bg-black/[0.06] font-medium text-[#1d1d1f]"
                )}
              >
                1. 데이터 수집
              </Link>
              <Link
                href="/portfolio/titanic/data-analysis"
                className={cn(
                  "hidden rounded-md px-2 py-1 text-xs text-[#1d1d1f]/80 hover:bg-black/[0.04] md:inline-flex",
                  pathname.startsWith("/portfolio/titanic/data-analysis") &&
                    "bg-black/[0.06] font-medium text-[#1d1d1f]"
                )}
              >
                2. 데이터 분석
              </Link>
              <Link
                href="/portfolio/titanic/data-modeling"
                className={cn(
                  "hidden rounded-md px-2 py-1 text-xs text-[#1d1d1f]/80 hover:bg-black/[0.04] md:inline-flex",
                  pathname.startsWith("/portfolio/titanic/data-modeling") &&
                    "bg-black/[0.06] font-medium text-[#1d1d1f]"
                )}
              >
                3. 데이터 모델링
              </Link>
            </div>
          </div>
        ) : null}
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialView={authView}
      />
    </>
  );
}
