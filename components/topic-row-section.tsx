"use client";

import Link from "next/link";
import RestaurantCard from "@/components/restaurant-card";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

export type TopicRowData = {
  slug: string;
  title: string;
  subtitle: string;
  emoji: string;
  category_slug?: string | null;
  category_label?: string | null;
  /** false면 행 제목을 주제 페이지로 링크하지 않음 */
  link_title?: boolean;
  restaurants: {
    rank: number;
    id: number;
    name: string;
    district: string;
    description: string;
    image_url: string;
    view_count?: number;
    category_slug?: string;
    category_label?: string;
    distance_km?: number | null;
    detail_href?: string | null;
  }[];
};

type TopicRowSectionProps = {
  row: TopicRowData;
  /** 행 제목 옆 카테고리 뱃지 (카테고리 전용 페이지) */
  showCategory?: boolean;
  /** 카드에 장르 표시 (메인 혼합 피드) */
  showCategoryOnCards?: boolean;
};

const CAROUSEL_ARROW_CLASS =
  "top-1/2 z-20 size-9 -translate-y-1/2 rounded-full border-0 bg-black/75 text-white shadow-lg backdrop-blur-sm hover:bg-black/90 disabled:pointer-events-none disabled:opacity-0";

export default function TopicRowSection({
  row,
  showCategory = false,
  showCategoryOnCards = false,
}: TopicRowSectionProps) {
  if (!row.restaurants.length) return null;

  const rowKey =
    showCategory && row.category_slug
      ? `${row.category_slug}-${row.slug}`
      : row.slug;

  const showArrows = row.restaurants.length > 1;

  return (
    <section className="mb-8" aria-labelledby={`topic-${rowKey}`}>
      <div className="mb-3 px-4 md:px-6 lg:px-8">
        <div className="flex flex-wrap items-center gap-2">
          <h2
            id={`topic-${rowKey}`}
            className="flex items-center gap-2 text-lg font-semibold text-white md:text-xl"
          >
            {row.link_title === false ? (
              <span className="flex items-center gap-2">
                <span className="text-xl" aria-hidden>
                  {row.emoji}
                </span>
                {row.title}
              </span>
            ) : (
              <Link
                href={`/topics/${row.slug}`}
                className="flex items-center gap-2 transition hover:text-white/80"
              >
                <span className="text-xl" aria-hidden>
                  {row.emoji}
                </span>
                {row.title}
              </Link>
            )}
          </h2>
          {showCategory && row.category_label && row.category_slug ? (
            <Link
              href={`/food/${row.category_slug}`}
              className="rounded-full bg-white/10 px-2.5 py-0.5 text-xs font-medium text-white/80 hover:bg-white/20"
            >
              {row.category_label}
            </Link>
          ) : null}
        </div>
        <p className="mt-0.5 text-sm text-white/55">{row.subtitle}</p>
      </div>

      <Carousel
        opts={{ align: "start", dragFree: true, containScroll: "trimSnaps" }}
        className="relative w-full px-4 md:px-6 lg:px-8"
      >
        <CarouselContent className="-ml-3 md:-ml-3">
          {row.restaurants.map((r) => (
            <CarouselItem
              key={`${rowKey}-${r.id}`}
              className="basis-[200px] pl-3 sm:basis-[220px]"
            >
              <RestaurantCard
                restaurant={{ ...r, rank: r.rank }}
                variant="dark"
                showCategoryLabel={showCategoryOnCards}
              />
            </CarouselItem>
          ))}
        </CarouselContent>
        {showArrows ? (
          <>
            <CarouselPrevious
              className={`${CAROUSEL_ARROW_CLASS} left-1 md:left-2`}
              aria-label="이전 맛집"
            />
            <CarouselNext
              className={`${CAROUSEL_ARROW_CLASS} right-1 md:right-2`}
              aria-label="다음 맛집"
            />
          </>
        ) : null}
      </Carousel>
    </section>
  );
}
