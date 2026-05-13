"use client";

import { useState } from "react";
import { User, LogIn, Briefcase } from "lucide-react";
import Link from "next/link";
import AuthModal from "./auth-modal";

export default function Header() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");

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
        <div className="flex items-center gap-8">
          <h1 className="text-2xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
              Whoareryu
            </span>
          </h1>
          
          <Link
            href="/portfolio"
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-foreground/70 hover:text-foreground border border-border hover:border-primary/50 rounded-lg transition-all"
          >
            <Briefcase className="w-4 h-4" />
            Portfolio
          </Link>
        </div>

        <nav className="flex items-center gap-4">
          <button
            onClick={openLogin}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-foreground/80 hover:text-foreground transition-colors"
          >
            <LogIn className="w-4 h-4" />
            Login
          </button>
          <button
            onClick={openSignup}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <User className="w-4 h-4" />
            Sign Up
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
