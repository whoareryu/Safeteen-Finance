/** 장르별 그라디언트(위→아래)·이모지 — 카드 공용 (기획서 식당 카드 사양). */

export type GenreStyle = { gradient: string; emoji: string };

const BY_SLUG: Record<string, GenreStyle> = {
  hansik: { gradient: "from-[#FF6B35] to-[#FF8C42]", emoji: "🍲" },
  jungsik: { gradient: "from-[#C0392B] to-[#E74C3C]", emoji: "🥢" },
  ilsik: { gradient: "from-[#2C3E50] to-[#34495E]", emoji: "🍣" },
  yangsik: { gradient: "from-[#1A5276] to-[#2980B9]", emoji: "🍝" },
  bunsik: { gradient: "from-[#F39C12] to-[#F1C40F]", emoji: "🍜" },
  bar: { gradient: "from-[#4A235A] to-[#7D3C98]", emoji: "🍺" },
  "cafe-dessert": { gradient: "from-[#6F4E37] to-[#A0522D]", emoji: "☕" },
  asian: { gradient: "from-[#1E8449] to-[#27AE60]", emoji: "🍛" },
  etc: { gradient: "from-[#616A6B] to-[#839192]", emoji: "🍽️" },
};

// 라벨(한글) → slug 별칭 (백엔드 food_categories.label: 바·카페·디저트 등 포함)
const LABEL_TO_SLUG: Record<string, string> = {
  한식: "hansik",
  중식: "jungsik",
  일식: "ilsik",
  양식: "yangsik",
  분식: "bunsik",
  술집: "bar",
  바: "bar",
  카페: "cafe-dessert",
  "카페·디저트": "cafe-dessert",
  아시안: "asian",
  기타: "etc",
};

const FALLBACK = BY_SLUG.etc;

/** slug 우선, 없으면 label로 장르 스타일 조회. 미매칭 시 '기타'. */
export function genreStyle(opts: {
  slug?: string | null;
  label?: string | null;
}): GenreStyle {
  if (opts.slug) {
    const bySlug = BY_SLUG[opts.slug];
    if (bySlug) return bySlug;
  }
  if (opts.label) {
    const slug = LABEL_TO_SLUG[opts.label];
    if (slug && BY_SLUG[slug]) return BY_SLUG[slug];
  }
  return FALLBACK;
}
