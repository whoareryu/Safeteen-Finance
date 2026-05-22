/** 백엔드 없이 Vercel에서 홈·데일리픽 UI 테스트용 목 데이터 */

export type MockTopicDef = {
  slug: string;
  title: string;
  subtitle: string;
  emoji: string;
  keywords: string[];
  category_slug?: string;
  category_label?: string;
};

const FOOD_IMAGES = [
  "https://images.unsplash.com/photo-1546069901-ba9599a1e63f?w=800&q=80",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&q=80",
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80",
  "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80",
  "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=800&q=80",
];

const DISTRICTS = [
  "강남구 역삼동",
  "마포구 연남동",
  "종로구 익선동",
  "용산구 이태원",
  "성동구 성수동",
  "송파구 잠실",
];

export const MOCK_HOME_TOPICS: MockTopicDef[] = [
  {
    slug: "value-picks",
    title: "가성비 맛집",
    subtitle: "부담 없이 즐기는 가격 대비 만족도",
    emoji: "💰",
    keywords: ["가성비", "저렴"],
  },
  {
    slug: "date-spots",
    title: "데이트 명소",
    subtitle: "분위기와 서비스가 좋은 로맨틱 스팟",
    emoji: "💑",
    keywords: ["데이트", "커플"],
  },
  {
    slug: "late-night-bites",
    title: "야장·술안주",
    subtitle: "밤늦게까지, 안주 한 잔",
    emoji: "🌙",
    keywords: ["야식", "안주"],
  },
  {
    slug: "hangover-cure",
    title: "해장 맛집",
    subtitle: "숙취에도 든든한 국물",
    emoji: "🍲",
    keywords: ["해장", "국밥"],
  },
  {
    slug: "solo-dining",
    title: "혼밥하기 좋은",
    subtitle: "혼자 와도 부담 없는 자리",
    emoji: "🧑",
    keywords: ["혼밥"],
  },
  {
    slug: "hanjeongsik",
    title: "한정식·코스",
    subtitle: "제철 나물과 정갈한 상차림",
    emoji: "🍱",
    keywords: ["한정식"],
    category_slug: "hansik",
    category_label: "한식",
  },
  {
    slug: "ramen-noodles",
    title: "라면·우동",
    subtitle: "따끈한 국물 한 그릇",
    emoji: "🍜",
    keywords: ["라면", "우동"],
    category_slug: "ilsik",
    category_label: "일식",
  },
  {
    slug: "dim-sum",
    title: "딤섬·중식",
    subtitle: "피자 한 바구니",
    emoji: "🥟",
    keywords: ["딤섬", "중식"],
    category_slug: "jungsik",
    category_label: "중식",
  },
  {
    slug: "brunch",
    title: "브런치",
    subtitle: "느긋한 주말 아침",
    emoji: "🥐",
    keywords: ["브런치"],
    category_slug: "yangsik",
    category_label: "양식",
  },
  {
    slug: "spicy-lovers",
    title: "매운맛",
    subtitle: "얼큰·화끈한 한 끼",
    emoji: "🌶️",
    keywords: ["매운", "얼큰"],
  },
  {
    slug: "rainy-day",
    title: "비 오는 날 추천",
    subtitle: "따뜻한 국물·실내",
    emoji: "🌧️",
    keywords: ["비", "국물"],
  },
  {
    slug: "group-dining",
    title: "단체·회식",
    subtitle: "여럿이 모이기 좋은",
    emoji: "👥",
    keywords: ["회식", "단체"],
  },
];

function hash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export function mockRestaurantsForTopic(
  topic: MockTopicDef,
  count: number,
  startRank = 1
) {
  const label = topic.category_label ?? "맛집";
  return Array.from({ length: count }, (_, i) => {
    const n = startRank + i;
    const id = 10000 + hash(`${topic.slug}-${n}`) % 80000;
    return {
      id,
      name: `${topic.emoji} ${topic.title} 맛집 ${n}호점`,
      image_url: FOOD_IMAGES[(n + hash(topic.slug)) % FOOD_IMAGES.length]!,
      district: DISTRICTS[(n + id) % DISTRICTS.length]!,
      distance_km: Math.round(((n % 7) + 0.3) * 10) / 10,
      rank: n,
      category_slug: topic.category_slug ?? null,
      category_label: label,
    };
  });
}

export function filterTopicsByQuery(q: string | null | undefined): MockTopicDef[] {
  const needle = (q ?? "").trim().toLowerCase();
  if (!needle) return MOCK_HOME_TOPICS;
  return MOCK_HOME_TOPICS.filter((t) => {
    const hay = `${t.title} ${t.subtitle} ${t.slug} ${t.keywords.join(" ")}`.toLowerCase();
    return hay.includes(needle);
  });
}
