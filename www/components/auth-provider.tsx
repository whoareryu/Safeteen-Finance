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
  isAdmin,
  loadStoredUser,
  saveStoredUser,
  googleLogin as apiGoogleLogin,
  updateNickname as apiUpdateNickname,
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
  googleLogin: (credential: string) => Promise<void>;
  logout: () => void;
  /** Naver·Kakao 팝업 로그인 완료 후 세션을 다시 읽어 상태를 갱신한다. */
  refreshSession: () => Promise<void>;
  updateNickname: (nickname: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);
  const [isOwner, setIsOwner] = useState(false);

  // httpOnly wr_session 쿠키(JWT+Redis)가 진짜 소스 — localStorage는 새로고침 사이
  // 깜빡임을 줄이기 위한 화면용 캐시일 뿐이라 세션으로 항상 덮어쓴다.
  const refreshSession = useCallback(async () => {
    const sessionUser = await fetchSession();
    saveStoredUser(sessionUser);
    setUser(sessionUser);
    setIsOwner(sessionUser ? await checkOwner() : false);
  }, []);

  useEffect(() => {
    setUser(loadStoredUser());
    refreshSession().then(() => setReady(true));
  }, [refreshSession]);

  const googleLogin = useCallback(
    async (credential: string) => {
      const result = await apiGoogleLogin(credential);
      if (result.pending) {
        // 신규 가입자 — 계정 생성 전 닉네임 설정·약관 동의 화면으로 이동.
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

  const updateNickname = useCallback(async (nickname: string) => {
    const u = await apiUpdateNickname(nickname);
    saveStoredUser(u);
    setUser(u);
  }, []);

  const value = useMemo(
    () => ({ user, ready, isOwner, googleLogin, logout, refreshSession, updateNickname }),
    [user, ready, isOwner, googleLogin, logout, refreshSession, updateNickname]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
