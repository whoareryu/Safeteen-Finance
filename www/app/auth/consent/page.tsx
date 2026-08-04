"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { checkNicknameAvailable, completeConsent, WR_AUTH_COMPLETE_MESSAGE } from "@/lib/auth";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";

function ConsentForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const email = searchParams.get("email") ?? "";
  const suggestedNickname = searchParams.get("nickname") ?? "";

  const [nickname, setNickname] = useState(suggestedNickname);
  const [nicknameChecked, setNicknameChecked] = useState(false);
  const [nicknameAvailable, setNicknameAvailable] = useState<boolean | null>(null);
  const [nicknameHint, setNicknameHint] = useState<string | null>(null);
  const [checkingNickname, setCheckingNickname] = useState(false);

  const [agreeTerms, setAgreeTerms] = useState(false);
  const [agreePrivacy, setAgreePrivacy] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const allAgreed = agreeTerms && agreePrivacy;
  const canSubmit = nicknameChecked && nicknameAvailable === true && allAgreed;

  function toggleAll(checked: boolean) {
    setAgreeTerms(checked);
    setAgreePrivacy(checked);
  }

  function handleNicknameChange(value: string) {
    setNickname(value);
    setNicknameChecked(false);
    setNicknameAvailable(null);
    setNicknameHint(null);
  }

  async function handleCheckNickname() {
    const nick = nickname.trim();
    if (!nick) {
      setNicknameHint("닉네임을 입력해 주세요.");
      return;
    }
    setCheckingNickname(true);
    try {
      const result = await checkNicknameAvailable(nick);
      setNicknameChecked(true);
      setNicknameAvailable(result.available);
      setNicknameHint(result.message);
    } catch (e) {
      setNicknameChecked(false);
      setNicknameAvailable(null);
      setNicknameHint(e instanceof Error ? e.message : "닉네임 확인에 실패했습니다.");
    } finally {
      setCheckingNickname(false);
    }
  }

  async function handleSubmit() {
    if (!token || !canSubmit) return;
    setSubmitting(true);
    setError(null);
    try {
      await completeConsent(token, nickname.trim(), true);
      if (window.opener) {
        window.opener.postMessage({ type: WR_AUTH_COMPLETE_MESSAGE }, window.location.origin);
        window.close();
      } else {
        window.location.href = "/";
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "가입 처리에 실패했습니다.");
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="modal-panel mx-auto">
        <p className="text-center text-sm text-muted-foreground">
          잘못된 접근입니다. 로그인 화면에서 다시 시도해 주세요.
        </p>
        <Button asChild variant="outline" className="mt-6 w-full">
          <Link href="/">홈으로</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="modal-panel mx-auto">
      <h1 className="mb-1 text-center text-2xl font-bold">
        <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
          가입 정보 설정
        </span>
      </h1>
      {email && (
        <p className="mb-6 text-center text-sm text-muted-foreground">
          {email} 계정으로 가입을 계속합니다.
        </p>
      )}

      <div className="modal-divider mb-5" />

      <Label className="mb-1 block text-xs font-medium text-muted-foreground">닉네임</Label>
      <div className="flex gap-2">
        <Input
          type="text"
          value={nickname}
          onChange={(e) => handleNicknameChange(e.target.value)}
          placeholder="사용할 닉네임"
          className="min-w-0 flex-1"
        />
        <Button
          type="button"
          variant="outline"
          onClick={handleCheckNickname}
          disabled={checkingNickname || !nickname.trim()}
          className="shrink-0 text-xs"
        >
          {checkingNickname ? "확인 중…" : "중복확인"}
        </Button>
      </div>
      {nicknameHint ? (
        <p
          className={`mt-1 text-xs ${
            nicknameAvailable ? "text-emerald-500" : "text-destructive"
          }`}
        >
          {nicknameHint}
        </p>
      ) : null}

      <div className="modal-divider my-5" />

      <label className="mb-4 flex cursor-pointer items-center gap-2 text-sm font-semibold">
        <Checkbox checked={allAgreed} onCheckedChange={(checked) => toggleAll(checked === true)} />
        전체 동의하기
      </label>

      <div className="space-y-3 border-t border-neutral-200 pt-3">
        <label className="flex cursor-pointer items-center justify-between gap-2 text-sm">
          <span className="flex items-center gap-2">
            <Checkbox
              checked={agreeTerms}
              onCheckedChange={(checked) => setAgreeTerms(checked === true)}
            />
            <span>[필수] 이용약관 동의</span>
          </span>
          <Link href="/terms" target="_blank" className="text-xs text-muted-foreground underline">
            보기
          </Link>
        </label>

        <label className="flex cursor-pointer items-center justify-between gap-2 text-sm">
          <span className="flex items-center gap-2">
            <Checkbox
              checked={agreePrivacy}
              onCheckedChange={(checked) => setAgreePrivacy(checked === true)}
            />
            <span>[필수] 개인정보 수집 및 이용 동의</span>
          </span>
          <Link href="/privacy" target="_blank" className="text-xs text-muted-foreground underline">
            보기
          </Link>
        </label>
      </div>

      {error ? <p className="mt-4 text-sm text-red-500">{error}</p> : null}

      <Button
        type="button"
        disabled={!canSubmit || submitting}
        onClick={handleSubmit}
        className="mt-6 w-full"
      >
        {submitting ? "처리 중…" : "가입 완료"}
      </Button>
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
