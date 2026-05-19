import { Sparkles } from "lucide-react";
import CategoryBlockGrid from "./category-block-grid";
import TodaysPicksCarousel from "./todays-picks-carousel";

export default function GourmetMateHero() {
  return (
    <div className="gourmet-hero w-full">
      <div className="flex flex-col items-center text-center">
        <p className="mb-3 inline-flex items-center gap-1.5 text-xs font-medium uppercase tracking-[0.18em] text-[#86868b] md:text-sm">
          <Sparkles className="h-3.5 w-3.5 text-amber-500" aria-hidden />
          Seoul Dining · AI Guide
        </p>

        <h1 className="text-balance text-4xl font-bold tracking-tight text-[#1d1d1f] md:text-6xl lg:text-7xl">
          GourmetMate
        </h1>

        <p className="mt-3 text-lg font-medium text-[#1d1d1f] md:text-xl">
          서울 맛집, AI가 카테고리별로 찾아드립니다
        </p>

        <p className="mx-auto mt-4 max-w-2xl text-pretty text-base leading-relaxed text-[#6e6e73] md:text-lg">
          한식·일식·중식부터 카페·주점까지 원하는 장르를 고르고, AI와 대화하며
          검색·추천·메뉴·분위기 정보를 한곳에서 받아보세요.
        </p>

        <CategoryBlockGrid className="mx-auto mt-8 max-w-5xl" />
      </div>

      <div className="mt-10 w-full">
        <TodaysPicksCarousel />
      </div>
    </div>
  );
}
