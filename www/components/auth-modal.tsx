"use client";

import { useEffect, useState } from "react";
import { X, Lock, User, Mail, Eye, EyeOff, AtSign, MapPin } from "lucide-react";
import { GoogleLogin } from "@react-oauth/google";
import { checkNicknameAvailable, checkUsernameAvailable } from "@/lib/auth";
import { useAuth } from "./auth-provider";

type ModalView = "login" | "signup";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialView?: ModalView;
}

type AuthModalState = {
  view: ModalView;
  username: string;
  password: string;
  passwordConfirm: string;
  email: string;
  nickname: string;
  region: string;
  showPassword: boolean;
  showPasswordConfirm: boolean;
  error: string | null;
  submitting: boolean;
  usernameChecked: boolean;
  usernameAvailable: boolean | null;
  usernameHint: string | null;
  checkingUsername: boolean;
  nicknameAvailable: boolean | null;
  nicknameHint: string | null;
  checkingNickname: boolean;
};

function createInitialState(view: ModalView): AuthModalState {
  return {
    view,
    username: "",
    password: "",
    passwordConfirm: "",
    email: "",
    nickname: "",
    region: "",
    showPassword: false,
    showPasswordConfirm: false,
    error: null,
    submitting: false,
    usernameChecked: false,
    usernameAvailable: null,
    usernameHint: null,
    checkingUsername: false,
    nicknameAvailable: null,
    nicknameHint: null,
    checkingNickname: false,
  };
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
  const { login, signup, googleLogin } = useAuth();
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
  const [state, setState] = useState<AuthModalState>(() =>
    createInitialState(initialView)
  );

  const patch = (partial: Partial<AuthModalState>) => {
    setState((prev) => ({ ...prev, ...partial }));
  };

  const {
    view,
    username,
    password,
    passwordConfirm,
    email,
    nickname,
    region,
    showPassword,
    showPasswordConfirm,
    error,
    submitting,
    usernameChecked,
    usernameAvailable,
    usernameHint,
    checkingUsername,
    nicknameAvailable,
    nicknameHint,
    checkingNickname,
  } = state;

  const passwordMismatch =
    passwordConfirm.length > 0 && password !== passwordConfirm;

  useEffect(() => {
    if (isOpen) patch({ view: initialView });
  }, [isOpen, initialView]);

  useEffect(() => {
    if (!isOpen) return;
    patch({
      error: null,
      usernameChecked: false,
      usernameAvailable: null,
      usernameHint: null,
      nicknameAvailable: null,
      nicknameHint: null,
    });
  }, [isOpen, view]);

  useEffect(() => {
    if (view !== "signup" || !isOpen) return;
    const nick = nickname.trim();
    if (nick.length < 1) {
      patch({ nicknameAvailable: null, nicknameHint: null });
      return;
    }

    const timer = window.setTimeout(async () => {
      patch({ checkingNickname: true });
      try {
        const result = await checkNicknameAvailable(nick);
        patch({
          nicknameAvailable: result.available,
          nicknameHint: result.message,
        });
      } catch (e) {
        patch({
          nicknameAvailable: null,
          nicknameHint:
            e instanceof Error ? e.message : "닉네임 확인에 실패했습니다.",
        });
      } finally {
        patch({ checkingNickname: false });
      }
    }, 450);

    return () => window.clearTimeout(timer);
  }, [nickname, view, isOpen]);

  if (!isOpen) return null;

  const resetAndClose = () => {
    setState(createInitialState(initialView));
    onClose();
  };

  const openSignup = () => patch({ view: "signup", error: null });
  const openLogin = () => patch({ view: "login", error: null });

  const handleFieldChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const field =
      name === "password_confirm" ? "passwordConfirm" : name;
    const updates: Partial<AuthModalState> = {
      [field]: value,
    } as Partial<AuthModalState>;

    if (name === "username") {
      updates.usernameChecked = false;
      updates.usernameAvailable = null;
      updates.usernameHint = null;
    }
    if (name === "nickname") {
      updates.nicknameAvailable = null;
      updates.nicknameHint = null;
    }

    patch(updates);
  };

  const handleCheckUsername = async () => {
    const id = username.trim();
    if (id.length < 3) {
      patch({ error: "아이디는 3자 이상 입력해 주세요." });
      return;
    }
    patch({ checkingUsername: true, error: null });
    try {
      const result = await checkUsernameAvailable(id);
      patch({
        usernameChecked: true,
        usernameAvailable: result.available,
        usernameHint: result.message,
        error: null,
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "중복 확인에 실패했습니다.";
      patch({
        error: msg,
        usernameChecked: false,
        usernameAvailable: null,
        usernameHint: msg,
      });
    } finally {
      patch({ checkingUsername: false });
    }
  };

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const formProps = Object.fromEntries(formData.entries()) as {
      username: string;
      password: string;
    };

    patch({ submitting: true, error: null });
    try {
      await login(formProps.username.trim(), formProps.password);
      resetAndClose();
    } catch (err) {
      patch({
        error: err instanceof Error ? err.message : "로그인에 실패했습니다.",
      });
    } finally {
      patch({ submitting: false });
    }
  };

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const formProps = Object.fromEntries(formData.entries()) as {
      username: string;
      password: string;
      password_confirm: string;
      email: string;
      nickname: string;
      region: string;
    };
    const agreeTerms = formData.get("agree_terms") === "on";

    const id = formProps.username.trim();
    const nick = formProps.nickname.trim();
    const mail = formProps.email.trim();

    if (formProps.password !== formProps.password_confirm) {
      patch({ error: "비밀번호가 일치하지 않습니다." });
      return;
    }
    if (!agreeTerms) {
      patch({ error: "이용약관 및 개인정보처리방침에 동의해야 합니다." });
      return;
    }

    patch({ submitting: true, error: null });

    try {
      const idResult =
        usernameChecked && usernameAvailable === true
          ? { available: true, message: usernameHint ?? "사용 가능한 아이디입니다." }
          : await checkUsernameAvailable(id);

      patch({
        usernameChecked: true,
        usernameAvailable: idResult.available,
        usernameHint: idResult.message,
      });
      if (!idResult.available) return;

      const nickResult = await checkNicknameAvailable(nick);
      patch({
        nicknameAvailable: nickResult.available,
        nicknameHint: nickResult.message,
      });
      if (!nickResult.available) return;

      const region = formProps.region.trim();
      await signup({
        username: id,
        password: formProps.password,
        password_confirm: formProps.password_confirm,
        email: mail,
        nickname: nick,
        region: region.length > 0 ? region : undefined,
        agree_terms: agreeTerms,
      });
      resetAndClose();
    } catch (err) {
      patch({
        error: err instanceof Error ? err.message : "회원가입에 실패했습니다.",
      });
    } finally {
      patch({ submitting: false });
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
                    name="username"
                    autoComplete="username"
                    placeholder="아이디"
                    value={username}
                    onChange={handleFieldChange}
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
                    name="password"
                    autoComplete="current-password"
                    placeholder="비밀번호"
                    value={password}
                    onChange={handleFieldChange}
                    className={`${inputClass} pl-10 pr-10`}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => patch({ showPassword: !showPassword })}
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

            {googleClientId && (
              <>
                <div className="relative my-5 flex items-center gap-3">
                  <div className="modal-divider flex-1" />
                  <span className="shrink-0 text-xs text-muted-foreground">또는</span>
                  <div className="modal-divider flex-1" />
                </div>
                <div className="flex justify-center">
                  <GoogleLogin
                    onSuccess={async (res) => {
                      if (!res.credential) return;
                      patch({ submitting: true, error: null });
                      try {
                        await googleLogin(res.credential);
                        resetAndClose();
                      } catch (e) {
                        patch({ error: e instanceof Error ? e.message : "Google 로그인 실패" });
                      } finally {
                        patch({ submitting: false });
                      }
                    }}
                    onError={() => patch({ error: "Google 로그인에 실패했습니다." })}
                    useOneTap={false}
                    use_fedcm_for_button
                    itp_support
                    text="signin_with"
                  />
                </div>
                <div className="mt-2 flex flex-col gap-2">
                  <a
                    href="/api/auth/naver/login"
                    className="flex w-full items-center justify-center rounded-md bg-[#03C75A] py-3 text-sm font-medium text-white"
                  >
                    네이버로 로그인
                  </a>
                  <a
                    href="/api/auth/kakao/login"
                    className="flex w-full items-center justify-center rounded-md bg-[#FEE500] py-3 text-sm font-medium text-black"
                  >
                    카카오로 로그인
                  </a>
                </div>
              </>
            )}

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

            <form
              onSubmit={handleSignup}
              className="max-h-[70vh] space-y-3 overflow-y-auto pr-1"
            >
              <div>
                <FieldLabel>아이디</FieldLabel>
                <div className="flex gap-2">
                  <div className="relative min-w-0 flex-1">
                    <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      type="text"
                      name="username"
                      autoComplete="username"
                      placeholder="영문, 숫자, _ (3~32자)"
                      value={username}
                      onChange={handleFieldChange}
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
                    name="password"
                    autoComplete="new-password"
                    placeholder="6자 이상"
                    value={password}
                    onChange={handleFieldChange}
                    className={`${inputClass} pl-10 pr-10`}
                    minLength={6}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => patch({ showPassword: !showPassword })}
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
                    name="password_confirm"
                    autoComplete="new-password"
                    placeholder="비밀번호 다시 입력"
                    value={passwordConfirm}
                    onChange={handleFieldChange}
                    className={`${inputClass} pl-10 pr-10`}
                    minLength={6}
                    required
                  />
                  <button
                    type="button"
                    onClick={() =>
                      patch({ showPasswordConfirm: !showPasswordConfirm })
                    }
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
                    name="email"
                    autoComplete="email"
                    placeholder="example@email.com"
                    value={email}
                    onChange={handleFieldChange}
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
                    name="nickname"
                    autoComplete="nickname"
                    placeholder="표시 이름"
                    value={nickname}
                    onChange={handleFieldChange}
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

              <div>
                <FieldLabel>지역 (선택)</FieldLabel>
                <div className="relative">
                  <MapPin className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    name="region"
                    autoComplete="address-level2"
                    placeholder="예: 서울"
                    value={region}
                    onChange={handleFieldChange}
                    className={`${inputClass} pl-10`}
                  />
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  잎사귀 진단·날씨 알림에 사용돼요. 나중에 입력해도 괜찮아요.
                </p>
              </div>

              <label className="flex cursor-pointer items-start gap-2 text-xs text-muted-foreground">
                <input type="checkbox" name="agree_terms" required className="mt-0.5 h-4 w-4" />
                <span>
                  <a href="/terms" target="_blank" className="underline">
                    이용약관
                  </a>{" "}
                  및{" "}
                  <a href="/privacy" target="_blank" className="underline">
                    개인정보처리방침
                  </a>
                  에 동의합니다. (필수)
                </span>
              </label>

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

            {googleClientId && (
              <>
                <div className="relative my-4 flex items-center gap-3">
                  <div className="modal-divider flex-1" />
                  <span className="shrink-0 text-xs text-muted-foreground">또는</span>
                  <div className="modal-divider flex-1" />
                </div>
                <div className="flex justify-center">
                  <GoogleLogin
                    onSuccess={async (res) => {
                      if (!res.credential) return;
                      patch({ submitting: true, error: null });
                      try {
                        await googleLogin(res.credential);
                        resetAndClose();
                      } catch (e) {
                        patch({ error: e instanceof Error ? e.message : "Google 로그인 실패" });
                      } finally {
                        patch({ submitting: false });
                      }
                    }}
                    onError={() => patch({ error: "Google 로그인에 실패했습니다." })}
                    useOneTap={false}
                    use_fedcm_for_button
                    itp_support
                    text="signup_with"
                  />
                </div>
                <div className="mt-2 flex flex-col gap-2">
                  <a
                    href="/api/auth/naver/login"
                    className="flex w-full items-center justify-center rounded-md bg-[#03C75A] py-3 text-sm font-medium text-white"
                  >
                    네이버로 시작하기
                  </a>
                  <a
                    href="/api/auth/kakao/login"
                    className="flex w-full items-center justify-center rounded-md bg-[#FEE500] py-3 text-sm font-medium text-black"
                  >
                    카카오로 시작하기
                  </a>
                </div>
              </>
            )}

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
