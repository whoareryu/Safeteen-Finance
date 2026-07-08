"use client";

import Link from "next/link";
import MypageShell from "@/components/mypage-shell";
import { isAdmin, useAuth } from "@/components/auth-provider";

export default function MypagePage() {
  const { user } = useAuth();

  return (
    <MypageShell title="마이페이지">
      <section className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-medium text-[#1d1d1f]">내 계정</h2>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-[#6e6e73]">아이디</dt>
            <dd className="font-medium">{user?.username}</dd>
          </div>
          <div>
            <dt className="text-[#6e6e73]">닉네임</dt>
            <dd className="font-medium">{user?.nickname}</dd>
          </div>
          <div>
            <dt className="text-[#6e6e73]">이메일</dt>
            <dd className="font-medium">{user?.email}</dd>
          </div>
          <div>
            <dt className="text-[#6e6e73]">역할</dt>
            <dd className="font-medium">{user?.role ?? "user"}</dd>
          </div>
          {typeof user?.id === "number" ? (
            <div>
              <dt className="text-[#6e6e73]">회원 번호</dt>
              <dd className="font-medium">{user.id}</dd>
            </div>
          ) : null}
        </dl>
        {isAdmin(user) ? (
          <p className="mt-6 text-sm text-[#6e6e73]">
            관리자 메뉴에서 고객·매점을 관리할 수 있습니다.
          </p>
        ) : null}
      </section>

      <section className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-medium text-[#1d1d1f]">음식 선호도</h2>
        <p className="mt-1 text-sm text-[#6e6e73]">장르 순위, 식사량, 알레르기 등 선호도를 수정할 수 있어요.</p>
        <Link
          href="/onboarding?edit=1"
          className="mt-4 inline-block rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-white"
        >
          선호도 수정
        </Link>
      </section>
    </MypageShell>
  );
}
