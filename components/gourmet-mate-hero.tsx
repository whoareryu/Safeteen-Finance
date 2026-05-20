"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import GeminiChat from "./gemini-chat";
import GourmetNavSearch from "./gourmet-nav-search";
import HomeSearchResults from "./home-search-results";
import HomeTopicFeed from "./home-topic-feed";

export default function GourmetMateHero() {
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");

  useEffect(() => {
    const t = window.setTimeout(() => setDebouncedQuery(searchQuery.trim()), 300);
    return () => window.clearTimeout(t);
  }, [searchQuery]);

  const isSearching = debouncedQuery.length > 0;

  return (
    <div className="gourmet-hero w-full">
      <GourmetNavSearch value={searchQuery} onChange={setSearchQuery} />

      <div className="flex flex-col items-center bg-[#fbfbfd] px-4 pb-6 pt-6 text-center sm:px-6 md:pb-8 md:pt-8">
        <p className="mb-3 inline-flex items-center gap-1.5 text-xs font-medium uppercase tracking-[0.18em] text-[#86868b] md:text-sm">
          <Sparkles className="h-3.5 w-3.5 text-amber-500" aria-hidden />
          Seoul Dining · AI Guide
        </p>

        <h1 className="text-balance text-4xl font-bold tracking-tight text-[#1d1d1f] md:text-6xl lg:text-7xl">
          GourmetMate
        </h1>

        <p className="mt-3 text-lg font-medium text-[#1d1d1f] md:text-xl">
          서울 맛집, AI가 주제별로 찾아드립니다
        </p>

        <p className="mx-auto mt-4 max-w-2xl text-pretty text-base leading-relaxed text-[#6e6e73] md:text-lg">
          &quot;오늘 뭐 먹지?&quot; 고민은 이제 끝, 내 입맛을 가장 잘 아는 인공지능 미식
          파트너 &apos;gourmetmate&apos;를 만나보세요!
        </p>
      </div>

      {!isSearching ? (
        <div className="border-t border-black/[0.06] bg-[#fbfbfd] px-4 py-8 sm:px-6 md:py-10">
          <p className="mb-5 text-center text-xs font-medium uppercase tracking-[0.2em] text-[#86868b]">
            AI에게 바로 물어보기
          </p>
          <div className="home-apple-chat mx-auto w-full max-w-3xl">
            <GeminiChat variant="apple" />
          </div>
        </div>
      ) : null}

      {isSearching ? <HomeSearchResults query={debouncedQuery} /> : null}

      <HomeTopicFeed query={isSearching ? debouncedQuery : undefined} />
    </div>
  );
}
