"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { GoogleLogin } from "@react-oauth/google";
import { WR_AUTH_COMPLETE_MESSAGE } from "@/lib/auth";
import { useAuth } from "./auth-provider";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const { googleLogin, refreshSession } = useAuth();
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const resetAndClose = () => {
    setError(null);
    setSubmitting(false);
    onClose();
  };

  const openSocialPopup = (provider: "naver" | "kakao") => {
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
          {googleClientId && (
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={async (res) => {
                  if (!res.credential) return;
                  setSubmitting(true);
                  setError(null);
                  try {
                    await googleLogin(res.credential);
                    resetAndClose();
                  } catch (e) {
                    setError(e instanceof Error ? e.message : "Google 로그인 실패");
                  } finally {
                    setSubmitting(false);
                  }
                }}
                onError={() => setError("Google 로그인에 실패했습니다.")}
                useOneTap={false}
                use_fedcm_for_button
                itp_support
                size="large"
                width="384"
                text="signin_with"
              />
            </div>
          )}
          <button
            type="button"
            disabled={submitting}
            onClick={() => openSocialPopup("naver")}
            className="flex w-full items-center justify-center rounded-md bg-[#03C75A] py-3 text-sm font-medium text-white disabled:opacity-60"
          >
            네이버로 로그인
          </button>
          <button
            type="button"
            disabled={submitting}
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
