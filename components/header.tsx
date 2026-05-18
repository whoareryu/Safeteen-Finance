"use client";

import { useState } from "react";
import { LogIn, Home, LogOut } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import AuthModal from "./auth-modal";
import WeatherWidget from "./weather-widget";
import { useAuth } from "./auth-provider";

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

  return (
    <>
      <header className="site-header--light fixed top-0 left-0 right-0 z-50 flex items-center justify-between border-b px-6 py-2">
        <div className="relative z-10 flex min-w-0 items-center gap-4 md:gap-6">
          <h1 className="text-2xl font-bold tracking-tight">
            <Link
              href="/"
              className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent hover:opacity-90"
            >
              Whoareryu
            </Link>
          </h1>
          <Link
            href="/"
            className="btn-white flex items-center gap-1.5 px-3 py-2 text-sm font-semibold tracking-wide"
          >
            <Home className="h-4 w-4" aria-hidden />
            HOME
          </Link>
          {showWeather ? <WeatherWidget /> : null}
        </div>

        {ready && user ? (
          <p
            className="site-header-greeting pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 whitespace-nowrap px-2 text-center text-lg font-semibold tracking-tight text-muted-foreground sm:text-xl md:text-2xl"
            aria-live="polite"
          >
            Hello,{" "}
            <span className="text-foreground">{user.nickname}</span> 님
          </p>
        ) : null}

        <nav className="relative z-10 flex shrink-0 items-center gap-3">
          <Link href="/seoulmate" className="btn-white px-3 py-2 text-sm font-medium">
            SeoulMate
          </Link>
          <Link href="/titanic" className="btn-white px-3 py-2 text-sm font-medium">
            타이타닉
          </Link>
          {ready && user ? (
            <button
              type="button"
              onClick={logout}
              className="btn-white flex items-center gap-2 px-4 py-2 text-sm font-medium"
            >
              <LogOut className="h-4 w-4" />
              로그아웃
            </button>
          ) : (
            <button
              type="button"
              onClick={openLogin}
              className="btn-white flex items-center gap-2 px-4 py-2 text-sm font-medium"
            >
              <LogIn className="h-4 w-4" />
              로그인
            </button>
          )}
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
