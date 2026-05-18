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
import {
  loadStoredUser,
  login as apiLogin,
  saveStoredUser,
  signup as apiSignup,
  type AuthUser,
} from "@/lib/auth";

type AuthContextValue = {
  user: AuthUser | null;
  ready: boolean;
  login: (username: string, password: string) => Promise<void>;
  signup: (payload: {
    username: string;
    password: string;
    password_confirm: string;
    email: string;
    nickname: string;
  }) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setUser(loadStoredUser());
    setReady(true);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const u = await apiLogin(username, password);
    saveStoredUser(u);
    setUser(u);
  }, []);

  const signup = useCallback(
    async (payload: {
      username: string;
      password: string;
      password_confirm: string;
      email: string;
      nickname: string;
    }) => {
      const u = await apiSignup(payload);
      saveStoredUser(u);
      setUser(u);
    },
    []
  );

  const logout = useCallback(() => {
    saveStoredUser(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, ready, login, signup, logout }),
    [user, ready, login, signup, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
