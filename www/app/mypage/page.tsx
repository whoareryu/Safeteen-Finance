"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/components/auth-provider";
import { checkNicknameAvailable } from "@/lib/auth";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function MyPage() {
  const { user, ready, updateNickname } = useAuth();

  const [editing, setEditing] = useState(false);
  const [nickname, setNickname] = useState("");
  const [nicknameChecked, setNicknameChecked] = useState(false);
  const [nicknameAvailable, setNicknameAvailable] = useState<boolean | null>(null);
  const [nicknameHint, setNicknameHint] = useState<string | null>(null);
  const [checkingNickname, setCheckingNickname] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) setNickname(user.nickname);
  }, [user]);

  if (!ready) return null;

  if (!user) {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center">
        <p className="text-sm text-muted-foreground">로그인이 필요합니다.</p>
        <Button asChild variant="outline" className="mt-6">
          <Link href="/">홈으로</Link>
        </Button>
      </div>
    );
  }

  const isUnchanged = nickname.trim() === user.nickname;
  const canSave = isUnchanged || (nicknameChecked && nicknameAvailable === true);

  function startEditing() {
    setEditing(true);
    setError(null);
  }

  function cancelEditing() {
    setEditing(false);
    setNickname(user!.nickname);
    setNicknameChecked(false);
    setNicknameAvailable(null);
    setNicknameHint(null);
    setError(null);
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
    if (nick === user!.nickname) {
      setNicknameChecked(true);
      setNicknameAvailable(true);
      setNicknameHint("현재 사용 중인 닉네임입니다.");
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

  async function handleSave() {
    const nick = nickname.trim();
    if (!nick || !canSave) return;
    if (isUnchanged) {
      setEditing(false);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await updateNickname(nick);
      setEditing(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "닉네임 변경에 실패했습니다.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 py-24">
      <h1 className="mb-8 text-2xl font-bold">마이페이지</h1>

      <Card>
        <CardContent className="space-y-4">
        <div>
          <Label className="mb-1 block text-xs font-medium text-muted-foreground">이메일</Label>
          <p className="text-sm">{user.email}</p>
        </div>

        <div>
          <Label className="mb-1 block text-xs font-medium text-muted-foreground">닉네임</Label>
          {editing ? (
            <>
              <div className="flex gap-2">
                <Input
                  type="text"
                  value={nickname}
                  onChange={(e) => handleNicknameChange(e.target.value)}
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
              {error ? <p className="mt-1 text-xs text-destructive">{error}</p> : null}
              <div className="mt-3 flex gap-2">
                <Button
                  type="button"
                  onClick={handleSave}
                  disabled={!canSave || saving}
                  className="flex-1"
                >
                  {saving ? "저장 중…" : "저장"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={cancelEditing}
                  className="flex-1 text-muted-foreground"
                >
                  취소
                </Button>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-between">
              <p className="text-sm">{user.nickname}</p>
              <Button
                type="button"
                variant="link"
                onClick={startEditing}
                className="h-auto p-0 text-xs font-medium"
              >
                수정
              </Button>
            </div>
          )}
        </div>
        </CardContent>
      </Card>
    </div>
  );
}
