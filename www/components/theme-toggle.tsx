"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);
  if (!mounted) return <div className="h-6 w-[42px]" />;

  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      aria-label="테마 전환"
      className={`flex h-6 w-[42px] items-center justify-center rounded-full border transition-all ${
        isDark
          ? "border-white/10 bg-[#1a1a1a] hover:bg-[#252525]"
          : "border-black/10 bg-white shadow-sm hover:bg-[#f5f5f7]"
      }`}
    >
      {isDark ? (
        <span className="flex h-4 w-4 items-center justify-center rounded-full bg-yellow-400 shadow-[0_0_6px_rgba(250,204,21,0.45)]">
          <Sun size={10} strokeWidth={3} className="text-yellow-900" />
        </span>
      ) : (
        <Moon size={13} strokeWidth={2} className="text-[#1d1d1f]/60" />
      )}
    </button>
  );
}
