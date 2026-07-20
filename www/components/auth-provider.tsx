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
  fetchSession,
  logoutSession,
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
    region?: string;
    agree_terms: boolean;
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
    // httpOnly wr_session 쿠키(JWT+Redis)가 진짜 소스 — localStorage는 새로고침 사이
    // 깜빡임을 줄이기 위한 화면용 캐시일 뿐이라 세션으로 항상 덮어쓴다.
    setUser(loadStoredUser());
    (async () => {
      const sessionUser = await fetchSession();
      saveStoredUser(sessionUser);
      setUser(sessionUser);
      setReady(true);
      if (sessionUser) {
        checkOwner().then(setIsOwner);
      }
    })();
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
      region?: string;
      agree_terms: boolean;
    }) => {
      const u = await apiSignup(payload);
      saveStoredUser(u);
      setUser(u);
      router.push("/plant");
    },
    [router]
  );

  const googleLogin = useCallback(
    async (credential: string) => {
      const result = await apiGoogleLogin(credential);
      if (result.pending) {
        // 신규 가입자 — 계정 생성 전 약관 동의 화면으로 이동.
        const qs = new URLSearchParams({
          token: result.consent_token,
          email: result.email,
          nickname: result.nickname,
        });
        window.location.href = `/auth/consent?${qs.toString()}`;
        return;
      }
      // 세션 쿠키(wr_session·wr_owner_session)는 백엔드가 httpOnly Set-Cookie로 내려준다.
      saveStoredUser(result);
      setUser(result);
      setIsOwner(result.is_owner);
    },
    []
  );

  const logout = useCallback(() => {
    logoutSession();
    saveStoredUser(null);
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
