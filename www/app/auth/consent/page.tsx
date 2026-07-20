"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { completeConsent, WR_AUTH_COMPLETE_MESSAGE } from "@/lib/auth";

function ConsentForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const email = searchParams.get("email") ?? "";
  const nickname = searchParams.get("nickname") ?? "";

  const [agreeTerms, setAgreeTerms] = useState(false);
  const [agreePrivacy, setAgreePrivacy] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const allAgreed = agreeTerms && agreePrivacy;

  function toggleAll(checked: boolean) {
    setAgreeTerms(checked);
    setAgreePrivacy(checked);
  }

  async function handleSubmit() {
    if (!token || !allAgreed) return;
    setSubmitting(true);
    setError(null);
    try {
      await completeConsent(token, true);
      if (window.opener) {
        window.opener.postMessage({ type: WR_AUTH_COMPLETE_MESSAGE }, window.location.origin);
        window.close();
      } else {
        window.location.href = "/";
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "동의 처리에 실패했습니다.");
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="modal-panel mx-auto">
        <p className="text-center text-sm text-muted-foreground">
          잘못된 접근입니다. 로그인 화면에서 다시 시도해 주세요.
        </p>
        <Link href="/" className="btn-white mt-6 block w-full py-3 text-center text-sm font-medium">
          홈으로
        </Link>
      </div>
    );
  }

  return (
    <div className="modal-panel mx-auto">
      <h1 className="mb-1 text-center text-2xl font-bold">
        <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
          약관 동의
        </span>
      </h1>
      {(email || nickname) && (
        <p className="mb-6 text-center text-sm text-muted-foreground">
          {nickname ? `${nickname} ` : ""}
          {email}
          {email ? " 계정으로 " : ""}가입을 계속하려면 아래 약관에 동의해 주세요.
        </p>
      )}

      <div className="modal-divider mb-5" />

      <label className="mb-4 flex cursor-pointer items-center gap-2 text-sm font-semibold">
        <input
          type="checkbox"
          checked={allAgreed}
          onChange={(e) => toggleAll(e.target.checked)}
          className="h-4 w-4"
        />
        전체 동의하기
      </label>

      <div className="space-y-3 border-t border-neutral-200 pt-3">
        <label className="flex cursor-pointer items-center justify-between gap-2 text-sm">
          <span className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={agreeTerms}
              onChange={(e) => setAgreeTerms(e.target.checked)}
              className="h-4 w-4"
            />
            <span>[필수] 이용약관 동의</span>
          </span>
          <Link href="/terms" target="_blank" className="text-xs text-muted-foreground underline">
            보기
          </Link>
        </label>

        <label className="flex cursor-pointer items-center justify-between gap-2 text-sm">
          <span className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={agreePrivacy}
              onChange={(e) => setAgreePrivacy(e.target.checked)}
              className="h-4 w-4"
            />
            <span>[필수] 개인정보 수집 및 이용 동의</span>
          </span>
          <Link href="/privacy" target="_blank" className="text-xs text-muted-foreground underline">
            보기
          </Link>
        </label>
      </div>

      {error ? <p className="mt-4 text-sm text-red-500">{error}</p> : null}

      <button
        type="button"
        disabled={!allAgreed || submitting}
        onClick={handleSubmit}
        className="btn-white mt-6 w-full py-3 text-sm font-medium disabled:opacity-60"
      >
        {submitting ? "처리 중…" : "동의하고 계속하기"}
      </button>
    </div>
  );
}

export default function ConsentPage() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center p-4">
      <Suspense fallback={null}>
        <ConsentForm />
      </Suspense>
    </div>
  );
}
