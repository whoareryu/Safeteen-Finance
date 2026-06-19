"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/components/auth-provider";
import { useNearbyLocation } from "@/components/nearby-location-provider";
import { Sparkles, LayoutDashboard } from "lucide-react";
import GeminiChat from "./gemini-chat";
import GourmetNavSearch from "./gourmet-nav-search";
import HomeSearchResults from "./home-search-results";
import HomeTopicFeed from "./home-topic-feed";
import TodayDailyPick from "./today-daily-pick";

function homeSearchHref(query: string) {
  const trimmed = query.trim();
  return trimmed ? `/?q=${encodeURIComponent(trimmed)}` : "/";
}

export default function GourmetMateHero() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const { isNearbyMode } = useNearbyLocation();
  /** URL ?q= — Enter·추천 칩 확정 검색·홈 복귀의 단일 기준 */
  const committedQuery = (searchParams.get("q") ?? "").trim();
  /** 검색창에 보이는 글자 (입력 중에는 결과를 바꾸지 않음) */
  const [inputValue, setInputValue] = useState(committedQuery);

  useEffect(() => {
    setInputValue(committedQuery);
  }, [committedQuery]);

  const commitSearch = useCallback(
    (raw: string) => {
      const trimmed = raw.trim();
      if (!trimmed) return;
      router.replace(homeSearchHref(trimmed), { scroll: true });
    },
    [router]
  );

  const handleSubmit = useCallback(() => {
    commitSearch(inputValue);
  }, [commitSearch, inputValue]);

  const handleClearInput = useCallback(() => {
    setInputValue("");
  }, []);

  const handleSuggestionClick = useCallback(
    (term: string) => {
      commitSearch(term);
    },
    [commitSearch]
  );

  const isSearchMode = committedQuery.length > 0;

  return (
    <div className="gourmet-hero w-full">
      <GourmetNavSearch
        value={inputValue}
        onChange={setInputValue}
        onSubmit={handleSubmit}
        onClearInput={handleClearInput}
        onSuggestionClick={handleSuggestionClick}
      />

      <div className="flex flex-col items-center bg-[#fbfbfd] px-4 pb-6 pt-6 text-center sm:px-6 md:pb-8 md:pt-8">
        <p className="mb-3 inline-flex items-center gap-1.5 text-xs font-medium uppercase tracking-[0.18em] text-[#86868b] md:text-sm">
          <Sparkles className="h-3.5 w-3.5 text-amber-500" aria-hidden />
          Seoul Dining · AI Guide
        </p>

        <h1 className="text-balance text-4xl font-bold tracking-tight text-[#1d1d1f] md:text-6xl lg:text-7xl">
          GourmetMate
        </h1>

        <p className="mt-3 text-lg font-medium text-[#1d1d1f] md:text-xl">
          {user && isNearbyMode
            ? "내 주변 맛집을 가까운 순으로 추천합니다"
            : user
              ? "로그인 후 위치를 허용하면 주변 맛집을 우선 추천합니다"
              : "서울 맛집, AI가 주제별로 찾아드립니다"}
        </p>

        <p className="mx-auto mt-4 max-w-2xl text-pretty text-base leading-relaxed text-[#6e6e73] md:text-lg">
          &quot;오늘 뭐 먹지?&quot; 고민은 이제 끝, 내 입맛을 가장 잘 아는 인공지능 미식
          파트너 &apos;gourmetmate&apos;를 만나보세요!
        </p>

        <Link
          href="/admin"
          className="mt-5 inline-flex items-center gap-2 rounded-full border border-[#1d1d1f]/15 bg-white px-4 py-2 text-sm font-medium text-[#1d1d1f] shadow-sm transition hover:bg-[#f5f5f7]"
        >
          <LayoutDashboard size={15} />
          관리자
        </Link>

        {!isSearchMode ? (
          <div className="home-apple-chat mt-8 w-full max-w-3xl text-left">
            <p className="mb-5 text-center text-xs font-medium uppercase tracking-[0.2em] text-[#86868b]">
              AI에게 바로 물어보기
            </p>
            <GeminiChat
              variant="apple"
              apiPath="/api/gourmet/chat"
              inputPlaceholder="맛집·메뉴·분위기를 Gemini에게 물어보기"
            />
          </div>
        ) : null}
      </div>

      {isSearchMode ? <HomeSearchResults query={committedQuery} /> : null}

      {!isSearchMode ? <TodayDailyPick /> : null}

      <HomeTopicFeed query={isSearchMode ? committedQuery : undefined} />
    </div>
  );
}
