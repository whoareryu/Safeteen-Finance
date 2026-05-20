"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useAuth } from "@/components/auth-provider";
import type { UserCoords } from "@/lib/gourmet-location";

export type NearbyLocationStatus =
  | "idle"
  | "loading"
  | "granted"
  | "denied"
  | "unsupported";

type NearbyLocationContextValue = {
  coords: UserCoords | null;
  status: NearbyLocationStatus;
  /** 로그인 + 위치 허용 시 true */
  isNearbyMode: boolean;
};

const NearbyLocationContext = createContext<NearbyLocationContextValue>({
  coords: null,
  status: "idle",
  isNearbyMode: false,
});

export function NearbyLocationProvider({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth();
  const [coords, setCoords] = useState<UserCoords | null>(null);
  const [status, setStatus] = useState<NearbyLocationStatus>("idle");

  useEffect(() => {
    if (!ready || !user) {
      setCoords(null);
      setStatus("idle");
      return;
    }

    if (typeof navigator === "undefined" || !navigator.geolocation) {
      setCoords(null);
      setStatus("unsupported");
      return;
    }

    let cancelled = false;
    setStatus("loading");

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        if (cancelled) return;
        setCoords({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        });
        setStatus("granted");
      },
      () => {
        if (cancelled) return;
        setCoords(null);
        setStatus("denied");
      },
      { enableHighAccuracy: true, timeout: 12_000, maximumAge: 300_000 }
    );

    return () => {
      cancelled = true;
    };
  }, [ready, user?.id]);

  const value = useMemo(
    () => ({
      coords,
      status,
      isNearbyMode: Boolean(user && coords),
    }),
    [coords, status, user]
  );

  return (
    <NearbyLocationContext.Provider value={value}>
      {children}
    </NearbyLocationContext.Provider>
  );
}

export function useNearbyLocation() {
  return useContext(NearbyLocationContext);
}
