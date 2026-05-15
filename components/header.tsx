"use client";

import { useState } from "react";
import { User, LogIn, Home } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import AuthModal from "./auth-modal";
import WeatherWidget from "./weather-widget";

export default function Header() {
  const pathname = usePathname();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const showWeather = pathname === "/";

  const openLogin = () => {
    setAuthMode("login");
    setShowAuthModal(true);
  };

  const openSignup = () => {
    setAuthMode("signup");
    setShowAuthModal(true);
  };

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="flex items-center gap-4 md:gap-6">
          <h1 className="text-2xl font-bold tracking-tight">
            <Link href="/" className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent hover:opacity-90">
              Whoareryu
            </Link>
          </h1>
          <Link
            href="/"
            className="flex items-center gap-1.5 rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm font-semibold tracking-wide text-foreground hover:border-primary/50 hover:bg-secondary/70 transition-all"
          >
            <Home className="h-4 w-4" aria-hidden />
            HOME
          </Link>
          {showWeather ? <WeatherWidget /> : null}
        </div>

        <nav className="flex items-center gap-3">
          <Link
            href="/seoulmate"
            className="px-3 py-2 text-sm font-medium text-foreground/80 hover:text-foreground border border-border hover:border-primary/50 rounded-lg transition-all"
          >
            SeoulMate
          </Link>
          <Link
            href="/titanic"
            className="px-3 py-2 text-sm font-medium text-foreground/80 hover:text-foreground border border-border hover:border-primary/50 rounded-lg transition-all"
          >
            타이타닉
          </Link>
          <button
            onClick={openSignup}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <User className="w-4 h-4" />
            Sign Up
          </button>
          <button
            onClick={openLogin}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-foreground/80 hover:text-foreground transition-colors"
          >
            <LogIn className="w-4 h-4" />
            Login
          </button>
        </nav>
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        mode={authMode}
        setMode={setAuthMode}
      />
    </>
  );
}
