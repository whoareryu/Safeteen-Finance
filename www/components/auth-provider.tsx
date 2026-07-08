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
import { useRouter } from "next/navigation";
import {
  isAdmin,
  loadStoredUser,
  login as apiLogin,
  saveStoredUser,
  signup as apiSignup,
  googleLogin as apiGoogleLogin,
  checkOwner,
  type AuthUser,
  type UserRole,
} from "@/lib/auth";

export { isAdmin, type AuthUser, type UserRole };

type AuthContextValue = {
  user: AuthUser | null;
  ready: boolean;
  isOwner: boolean;
  login: (username: string, password: string) => Promise<void>;
  signup: (payload: {
    username: string;
    password: string;
    password_confirm: string;
    email: string;
    nickname: string;
  }) => Promise<void>;
  googleLogin: (credential: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);
  const [isOwner, setIsOwner] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const stored = loadStoredUser();
    setUser(stored);
    setReady(true);
    if (stored) {
      checkOwner().then(setIsOwner);
    }
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
      router.push("/onboarding");
    },
    [router]
  );

  const googleLogin = useCallback(
    async (credential: string) => {
      const u = await apiGoogleLogin(credential);
      saveStoredUser(u);
      document.cookie = `wr_session=${u.id}; path=/; SameSite=Lax; max-age=2592000`;
      if (u.owner_token) {
        document.cookie = `wr_owner_session=${u.owner_token}; path=/; SameSite=Lax; max-age=2592000`;
      } else {
        document.cookie = "wr_owner_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      }
      setUser(u);
      setIsOwner(!!u.owner_token);
    },
    []
  );

  const logout = useCallback(() => {
    saveStoredUser(null);
    document.cookie = "wr_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie = "wr_owner_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    setUser(null);
    setIsOwner(false);
  }, []);

  const value = useMemo(
    () => ({ user, ready, isOwner, login, signup, googleLogin, logout }),
    [user, ready, isOwner, login, signup, googleLogin, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
