export type CategoryBlockTheme = {
  emoji: string;
  /** 카드 배경 그라데이션 */
  bg: string;
  border: string;
  /** 제목·아이콘 색 */
  text: string;
  /** 호버 시 살짝 진해지는 배경 */
  hoverBg: string;
};

export type NavCategory = {
  slug: string;
  href: string;
  label: string;
  title: string;
  description: string;
  accent: string;
  block: CategoryBlockTheme;
};

export const CATEGORY_LINKS: NavCategory[] = [
  {
    slug: "hansik",
    href: "/food/hansik",
    label: "한식",
    title: "한식",
    description: "비빔밥, 찌개, 구이, 정식 — 한국의 맛과 정성을 담은 식탁.",
    accent: "from-red-700/90 via-rose-600/80 to-amber-500/70",
    block: {
      emoji: "🍚",
      bg: "bg-gradient-to-br from-red-100 via-orange-50 to-amber-50",
      hoverBg: "hover:from-red-200 hover:via-orange-100 hover:to-amber-100",
      border: "border-red-300/70",
      text: "text-red-950",
    },
  },
  {
    slug: "ilsik",
    href: "/food/ilsik",
    label: "일식",
    title: "일식",
    description: "스시, 라멘, 돈카츠, 이자카야 — 섬세한 일본 요리의 세계.",
    accent: "from-slate-700/90 via-red-800/75 to-rose-400/65",
    block: {
      emoji: "🍣",
      bg: "bg-gradient-to-br from-slate-200 via-rose-50 to-red-100",
      hoverBg: "hover:from-slate-300 hover:via-rose-100 hover:to-red-200",
      border: "border-slate-400/60",
      text: "text-slate-900",
    },
  },
  {
    slug: "jungsik",
    href: "/food/jungsik",
    label: "중식",
    title: "중식",
    description: "짜장, 탕수육, 훠궈, 딤섬 — 다채로운 중화요리의 풍미.",
    accent: "from-amber-800/90 via-red-600/75 to-yellow-500/65",
    block: {
      emoji: "🥟",
      bg: "bg-gradient-to-br from-amber-100 via-yellow-50 to-red-50",
      hoverBg: "hover:from-amber-200 hover:via-yellow-100 hover:to-red-100",
      border: "border-amber-400/70",
      text: "text-amber-950",
    },
  },
  {
    slug: "yangsik",
    href: "/food/yangsik",
    label: "양식",
    title: "양식",
    description: "파스타, 스테이크, 브런치 — 서양식 다이닝과 와인 페어링.",
    accent: "from-stone-700/90 via-amber-700/75 to-orange-400/65",
    block: {
      emoji: "🍝",
      bg: "bg-gradient-to-br from-stone-200 via-amber-50 to-orange-100",
      hoverBg: "hover:from-stone-300 hover:via-amber-100 hover:to-orange-200",
      border: "border-stone-400/60",
      text: "text-stone-900",
    },
  },
  {
    slug: "asian",
    href: "/food/asian",
    label: "아시안",
    title: "아시안",
    description: "태국, 베트남, 인도 등 — 동남아·남아시아의 향신 가득한 요리.",
    accent: "from-emerald-700/90 via-lime-600/75 to-teal-400/65",
    block: {
      emoji: "🍜",
      bg: "bg-gradient-to-br from-emerald-100 via-lime-50 to-teal-100",
      hoverBg: "hover:from-emerald-200 hover:via-lime-100 hover:to-teal-200",
      border: "border-emerald-400/70",
      text: "text-emerald-950",
    },
  },
  {
    slug: "bunsik",
    href: "/food/bunsik",
    label: "분식",
    title: "분식",
    description: "떡볶이, 김밥, 라면, 순대 — 편하고 든든한 한국식 간편식.",
    accent: "from-orange-600/90 via-red-500/75 to-yellow-400/70",
    block: {
      emoji: "🌶️",
      bg: "bg-gradient-to-br from-orange-100 via-red-50 to-yellow-100",
      hoverBg: "hover:from-orange-200 hover:via-red-100 hover:to-yellow-200",
      border: "border-orange-400/70",
      text: "text-orange-950",
    },
  },
  {
    slug: "cafe-dessert",
    href: "/food/cafe-dessert",
    label: "카페/디저트",
    title: "카페/디저트",
    description: "커피, 베이커리, 아이스크림 — 달콤한 휴식과 디저트 카페.",
    accent: "from-pink-600/90 via-fuchsia-500/75 to-violet-400/65",
    block: {
      emoji: "☕",
      bg: "bg-gradient-to-br from-pink-100 via-rose-50 to-violet-100",
      hoverBg: "hover:from-pink-200 hover:via-rose-100 hover:to-violet-200",
      border: "border-pink-300/70",
      text: "text-pink-950",
    },
  },
  {
    slug: "bar",
    href: "/food/bar",
    label: "바/주점",
    title: "바/주점",
    description: "칵테일, 와인바, 포차 — 밤의 분위기와 안주 한 잔.",
    accent: "from-indigo-900/95 via-purple-800/85 to-violet-600/70",
    block: {
      emoji: "🍸",
      bg: "bg-gradient-to-br from-indigo-950 via-purple-900 to-violet-800",
      hoverBg: "hover:from-indigo-900 hover:via-purple-800 hover:to-violet-700",
      border: "border-violet-500/50",
      text: "text-white",
    },
  },
];

export function getCategoryBySlug(slug: string): NavCategory | undefined {
  return CATEGORY_LINKS.find((c) => c.slug === slug);
}

export const PORTFOLIO_LINKS = [
  {
    href: "/portfolio/titanic",
    label: "타이타닉",
    tagline: "생존 예측 · 데이터 분석",
    theme: "titanic" as const,
  },
];
