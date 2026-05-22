"use client";

import { Star } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useFavorites } from "@/components/favorites-provider";
import { useAuth } from "@/components/auth-provider";

type FavoriteStarButtonProps = {
  storeId: number;
  className?: string;
  size?: "sm" | "md";
};

export default function FavoriteStarButton({
  storeId,
  className,
  size = "sm",
}: FavoriteStarButtonProps) {
  const { user, ready: authReady } = useAuth();
  const { isFavorited, toggle, ready: favReady } = useFavorites();
  const [busy, setBusy] = useState(false);

  if (!authReady || !user) return null;

  const active = favReady && isFavorited(storeId);
  const iconClass = size === "md" ? "h-5 w-5" : "h-4 w-4";

  return (
    <button
      type="button"
      disabled={busy || !favReady}
      aria-label={active ? "즐겨찾기 해제" : "즐겨찾기 추가"}
      aria-pressed={active}
      className={cn(
        "rounded-full bg-black/55 p-1.5 text-white shadow-sm backdrop-blur-sm transition hover:bg-black/70 disabled:opacity-50",
        className
      )}
      onClick={async (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (busy) return;
        setBusy(true);
        try {
          await toggle(storeId);
        } finally {
          setBusy(false);
        }
      }}
    >
      <Star
        className={cn(iconClass, active ? "fill-amber-400 text-amber-400" : "text-white/90")}
      />
    </button>
  );
}
