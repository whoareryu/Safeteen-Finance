"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { WR_AUTH_COMPLETE_MESSAGE } from "@/lib/auth";
import { useAuth } from "./auth-provider";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const { refreshSession } = useAuth();
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const resetAndClose = () => {
    setError(null);
    onClose();
  };

  // 구글도 네이버/카카오와 같은 팝업 + 서버측 인가코드 리다이렉트 방식으로 통일했다
  // (예전에는 구글만 프론트에서 ID 토큰을 바로 받아 POST하는 위젯 방식이었다).
  const openSocialPopup = (provider: "google" | "naver" | "kakao") => {
    // 콜백은 auth.whoareryu.cloud로 직접 오기 때문에, state 검증 쿠키가 같은
    // 도메인에 저장되도록 로그인 시작도 프록시(whoareryu.cloud) 대신 auth
    // 서비스 도메인으로 바로 연다 — 그렇지 않으면 콜백에서 쿠키를 못 읽는다.
    const authUrl = process.env.NEXT_PUBLIC_AUTH_URL || "https://auth.whoareryu.cloud";
    const popup = window.open(
      `${authUrl}/auth/${provider}/login`,
      "wr_oauth_popup",
      "width=480,height=720"
    );
    if (!popup) {
      setError("팝업이 차단되었습니다. 브라우저의 팝업 차단을 해제해 주세요.");
      return;
    }
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      if (event.data?.type !== WR_AUTH_COMPLETE_MESSAGE) return;
      window.removeEventListener("message", handleMessage);
      refreshSession().then(resetAndClose);
    };
    window.addEventListener("message", handleMessage);
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div className="modal-overlay absolute inset-0" onClick={resetAndClose} aria-hidden />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-modal-title"
        className="modal-panel"
      >
        <button
          type="button"
          onClick={resetAndClose}
          className="absolute right-4 top-4 rounded-lg border border-neutral-300 bg-neutral-50 p-2 text-neutral-600 transition-colors hover:border-neutral-400 hover:bg-neutral-100 hover:text-neutral-900"
          aria-label="닫기"
        >
          <X className="h-5 w-5" />
        </button>

        <h2 id="auth-modal-title" className="mb-6 text-center text-2xl font-bold">
          <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
            로그인
          </span>
        </h2>

        <div className="modal-divider mb-5" />

        {error ? (
          <p className="mb-4 text-center text-sm text-destructive" role="alert">
            {error}
          </p>
        ) : null}

        <div className="space-y-2">
          <button
            type="button"
            onClick={() => openSocialPopup("google")}
            className="flex w-full items-center justify-center gap-2 rounded-md border border-neutral-300 bg-white py-3 text-sm font-medium text-neutral-800 disabled:opacity-60"
          >
            <svg className="h-4 w-4" viewBox="0 0 48 48" aria-hidden="true">
              <path
                fill="#FFC107"
                d="M43.6 20.5H42V20H24v8h11.3C33.7 32.9 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.5 6.1 29.5 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.7-.4-3.5z"
              />
              <path
                fill="#FF3D00"
                d="M6.3 14.7l6.6 4.8C14.6 15.9 18.9 13 24 13c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.5 6.1 29.5 4 24 4c-7.7 0-14.3 4.3-17.7 10.7z"
              />
              <path
                fill="#4CAF50"
                d="M24 44c5.2 0 10-2 13.6-5.2l-6.3-5.3C29.2 35.4 26.7 36 24 36c-5.2 0-9.6-3.1-11.3-7.6l-6.5 5C9.6 39.6 16.3 44 24 44z"
              />
              <path
                fill="#1976D2"
                d="M43.6 20.5H42V20H24v8h11.3c-.8 2.3-2.3 4.3-4.1 5.7l6.3 5.3C41.5 35.6 44 30.3 44 24c0-1.3-.1-2.7-.4-3.5z"
              />
            </svg>
            구글로 로그인
          </button>
          <button
            type="button"
            onClick={() => openSocialPopup("naver")}
            className="flex w-full items-center justify-center rounded-md bg-[#03C75A] py-3 text-sm font-medium text-white disabled:opacity-60"
          >
            네이버로 로그인
          </button>
          <button
            type="button"
            onClick={() => openSocialPopup("kakao")}
            className="flex w-full items-center justify-center rounded-md bg-[#FEE500] py-3 text-sm font-medium text-black disabled:opacity-60"
          >
            카카오로 로그인
          </button>
        </div>
      </div>
    </div>
  );
}
