"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { fetchFavoriteStoreIds, toggleFavorite } from "@/lib/favorites";
import { useAuth } from "@/components/auth-provider";

type FavoritesContextValue = {
  favoritedIds: Set<number>;
  isFavorited: (storeId: number) => boolean;
  toggle: (storeId: number) => Promise<boolean>;
  refresh: () => Promise<void>;
  ready: boolean;
};

const FavoritesContext = createContext<FavoritesContextValue | null>(null);

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [favoritedIds, setFavoritedIds] = useState<Set<number>>(new Set());
  const [ready, setReady] = useState(false);

  const refresh = useCallback(async () => {
    if (!user?.username) {
      setFavoritedIds(new Set());
      setReady(true);
      return;
    }
    const ids = await fetchFavoriteStoreIds(user.id);
    setFavoritedIds(new Set(ids));
    setReady(true);
  }, [user?.username]);

  useEffect(() => {
    setReady(false);
    void refresh();
  }, [refresh]);

  const toggle = useCallback(
    async (storeId: number) => {
      if (!user?.username) return false;
      const { favorited } = await toggleFavorite(user.id, storeId);
      setFavoritedIds((prev) => {
        const next = new Set(prev);
        if (favorited) next.add(storeId);
        else next.delete(storeId);
        return next;
      });
      return favorited;
    },
    [user?.username]
  );

  const isFavorited = useCallback(
    (storeId: number) => favoritedIds.has(storeId),
    [favoritedIds]
  );

  const value = useMemo(
    () => ({ favoritedIds, isFavorited, toggle, refresh, ready }),
    [favoritedIds, isFavorited, toggle, refresh, ready]
  );

  return (
    <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
  );
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext);
  if (!ctx) throw new Error("useFavorites must be used within FavoritesProvider");
  return ctx;
}
