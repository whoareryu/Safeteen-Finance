"use client";

import { useEffect, useState } from "react";
import { X, Lock, User, Mail, Eye, EyeOff, AtSign } from "lucide-react";
import { checkNicknameAvailable, checkUsernameAvailable } from "@/lib/auth";
import { useAuth } from "./auth-provider";

type ModalView = "login" | "signup";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialView?: ModalView;
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <label className="mb-1 block text-xs font-medium text-muted-foreground">
      {children}
    </label>
  );
}

const inputClass = "input-light";

export default function AuthModal({
  isOpen,
  onClose,
  initialView = "login",
}: AuthModalProps) {
  const { login, signup } = useAuth();
  const [view, setView] = useState<ModalView>(initialView);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [email, setEmail] = useState("");
  const [nickname, setNickname] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [usernameChecked, setUsernameChecked] = useState(false);
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(null);
  const [usernameHint, setUsernameHint] = useState<string | null>(null);
  const [checkingUsername, setCheckingUsername] = useState(false);

  const [nicknameAvailable, setNicknameAvailable] = useState<boolean | null>(null);
  const [nicknameHint, setNicknameHint] = useState<string | null>(null);
  const [checkingNickname, setCheckingNickname] = useState(false);

  const passwordMismatch =
    passwordConfirm.length > 0 && password !== passwordConfirm;

  useEffect(() => {
    if (isOpen) setView(initialView);
  }, [isOpen, initialView]);

  useEffect(() => {
    if (!isOpen) return;
    setError(null);
    setUsernameChecked(false);
    setUsernameAvailable(null);
    setUsernameHint(null);
    setNicknameAvailable(null);
    setNicknameHint(null);
  }, [isOpen, view]);

  useEffect(() => {
    if (view !== "signup" || !isOpen) return;
    const nick = nickname.trim();
    if (nick.length < 1) {
      setNicknameAvailable(null);
      setNicknameHint(null);
      return;
    }

    const timer = window.setTimeout(async () => {
      setCheckingNickname(true);
      try {
        const result = await checkNicknameAvailable(nick);
        setNicknameAvailable(result.available);
        setNicknameHint(result.message);
      } catch (e) {
        setNicknameAvailable(null);
        setNicknameHint(
          e instanceof Error ? e.message : "닉네임 확인에 실패했습니다."
        );
      } finally {
        setCheckingNickname(false);
      }
    }, 450);

    return () => window.clearTimeout(timer);
  }, [nickname, view, isOpen]);

  if (!isOpen) return null;

  const resetAndClose = () => {
    setUsername("");
    setPassword("");
    setPasswordConfirm("");
    setEmail("");
    setNickname("");
    setError(null);
    onClose();
  };

  const openSignup = () => {
    setView("signup");
    setError(null);
  };

  const openLogin = () => {
    setView("login");
    setError(null);
  };

  const handleCheckUsername = async () => {
    const id = username.trim();
    if (id.length < 3) {
      setError("아이디는 3자 이상 입력해 주세요.");
      return;
    }
    setCheckingUsername(true);
    setError(null);
    try {
      const result = await checkUsernameAvailable(id);
      setUsernameChecked(true);
      setUsernameAvailable(result.available);
      setUsernameHint(result.message);
      if (!result.available) {
        setError(null);
      } else {
        setError(null);
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "중복 확인에 실패했습니다.";
      setError(msg);
      setUsernameChecked(false);
      setUsernameAvailable(null);
      setUsernameHint(msg);
    } finally {
      setCheckingUsername(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(username.trim(), password);
      resetAndClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    const id = username.trim();
    const nick = nickname.trim();
    const mail = email.trim();

    if (password !== passwordConfirm) {
      setError(null);
      return;
    }

    window.alert(
      [
        "입력하신 내용",
        "",
        `아이디: ${id}`,
        `비밀번호: ${password}`,
        `비밀번호 확인: ${passwordConfirm}`,
        `이메일: ${mail}`,
        `닉네임: ${nick}`,
      ].join("\n")
    );

    setSubmitting(true);
    setError(null);

    try {
      const idResult =
        usernameChecked && usernameAvailable === true
          ? { available: true, message: usernameHint ?? "사용 가능한 아이디입니다." }
          : await checkUsernameAvailable(id);

      setUsernameChecked(true);
      setUsernameAvailable(idResult.available);
      setUsernameHint(idResult.message);
      if (!idResult.available) return;

      const nickResult = await checkNicknameAvailable(nick);
      setNicknameAvailable(nickResult.available);
      setNicknameHint(nickResult.message);
      if (!nickResult.available) return;

      await signup({
        username: id,
        password,
        password_confirm: passwordConfirm,
        email: mail,
        nickname: nick,
      });
      resetAndClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "회원가입에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
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

        {view === "login" ? (
          <>
            <h2
              id="auth-modal-title"
              className="mb-6 text-center text-2xl font-bold"
            >
              <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
                로그인
              </span>
            </h2>

            <div className="modal-divider mb-5" />

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <FieldLabel>아이디</FieldLabel>
                <div className="relative">
                  <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    autoComplete="username"
                    placeholder="아이디"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className={`${inputClass} pl-10`}
                    required
                  />
                </div>
              </div>

              <div>
                <FieldLabel>비밀번호</FieldLabel>
                <div className="relative">
                  <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    placeholder="비밀번호"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={`${inputClass} pl-10 pr-10`}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    aria-label={showPassword ? "비밀번호 숨기기" : "비밀번호 보기"}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {error ? (
                <p className="text-sm text-destructive" role="alert">
                  {error}
                </p>
              ) : null}

              <button
                type="submit"
                disabled={submitting}
                className="btn-white w-full py-3 text-sm font-medium disabled:opacity-60"
              >
                {submitting ? "로그인 중…" : "로그인"}
              </button>
            </form>

            <div className="modal-divider my-5" />

            <p className="text-center text-sm text-muted-foreground">
              아이디가 없으신가요?{" "}
              <button
                type="button"
                onClick={openSignup}
                className="font-medium text-primary hover:underline"
              >
                회원가입
              </button>
            </p>
          </>
        ) : (
          <>
            <h2
              id="auth-modal-title"
              className="mb-6 text-center text-2xl font-bold"
            >
              <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
                회원가입
              </span>
            </h2>

            <form onSubmit={handleSignup} className="max-h-[70vh] space-y-3 overflow-y-auto pr-1">
              <div>
                <FieldLabel>아이디</FieldLabel>
                <div className="flex gap-2">
                  <div className="relative min-w-0 flex-1">
                    <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      type="text"
                      autoComplete="username"
                      placeholder="영문, 숫자, _ (3~32자)"
                      value={username}
                      onChange={(e) => {
                        setUsername(e.target.value);
                        setUsernameChecked(false);
                        setUsernameAvailable(null);
                        setUsernameHint(null);
                      }}
                      className={`${inputClass} pl-10`}
                      required
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleCheckUsername}
                    disabled={checkingUsername || username.trim().length < 3}
                    className="btn-white shrink-0 px-3 py-2 text-xs font-medium disabled:opacity-50"
                  >
                    {checkingUsername ? "확인 중…" : "중복확인"}
                  </button>
                </div>
                {usernameHint ? (
                  <p
                    className={`mt-1 text-xs ${
                      usernameAvailable ? "text-emerald-500" : "text-destructive"
                    }`}
                  >
                    {usernameHint}
                  </p>
                ) : null}
              </div>

              <div>
                <FieldLabel>비밀번호</FieldLabel>
                <div className="relative">
                  <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type={showPassword ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="6자 이상"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={`${inputClass} pl-10 pr-10`}
                    minLength={6}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <FieldLabel>비밀번호 확인</FieldLabel>
                <div className="relative">
                  <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type={showPasswordConfirm ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="비밀번호 다시 입력"
                    value={passwordConfirm}
                    onChange={(e) => setPasswordConfirm(e.target.value)}
                    className={`${inputClass} pl-10 pr-10`}
                    minLength={6}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPasswordConfirm ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
                {passwordMismatch ? (
                  <p className="mt-1 text-xs text-destructive" role="alert">
                    비밀번호가 일치하지 않습니다.
                  </p>
                ) : null}
              </div>

              <div>
                <FieldLabel>이메일 주소</FieldLabel>
                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="email"
                    autoComplete="email"
                    placeholder="example@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={`${inputClass} pl-10`}
                    required
                  />
                </div>
              </div>

              <div>
                <FieldLabel>사용할 닉네임</FieldLabel>
                <div className="relative">
                  <AtSign className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    autoComplete="nickname"
                    placeholder="표시 이름"
                    value={nickname}
                    onChange={(e) => {
                      setNickname(e.target.value);
                      setNicknameAvailable(null);
                      setNicknameHint(null);
                    }}
                    className={`${inputClass} pl-10`}
                    required
                  />
                </div>
                {checkingNickname && nickname.trim() ? (
                  <p className="mt-1 text-xs text-muted-foreground">닉네임 확인 중…</p>
                ) : null}
                {nicknameAvailable === false ? (
                  <p className="mt-1 text-xs text-destructive">사용중인 닉네임입니다.</p>
                ) : null}
                {nicknameAvailable === true && nicknameHint ? (
                  <p className="mt-1 text-xs text-emerald-500">{nicknameHint}</p>
                ) : null}
              </div>

              {error ? (
                <p className="text-sm text-destructive" role="alert">
                  {error}
                </p>
              ) : null}

              <button
                type="submit"
                disabled={submitting}
                className="btn-white w-full py-3 text-sm font-medium disabled:opacity-60"
              >
                {submitting ? "가입 중…" : "회원가입"}
              </button>
            </form>

            <p className="mt-4 text-center text-sm text-muted-foreground">
              이미 계정이 있으신가요?{" "}
              <button
                type="button"
                onClick={openLogin}
                className="font-medium text-primary hover:underline"
              >
                로그인
              </button>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
