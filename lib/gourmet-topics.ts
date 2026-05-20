/** 메인 홈 주제 행 — backend COMMON_TOPICS 와 slug 동기화 */

export type GourmetTopic = {
  slug: string;
  href: string;
  title: string;
  subtitle: string;
  emoji: string;
};

export const HOME_TOPIC_LINKS: GourmetTopic[] = [
  {
    slug: "value-picks",
    href: "/topics/value-picks",
    title: "가성비 맛집",
    subtitle: "부담 없이 즐기는 가격 대비 만족도",
    emoji: "💰",
  },
  {
    slug: "date-spots",
    href: "/topics/date-spots",
    title: "데이트 명소",
    subtitle: "분위기와 서비스가 좋은 로맨틱 스팟",
    emoji: "💑",
  },
  {
    slug: "late-night-bites",
    href: "/topics/late-night-bites",
    title: "야장·술안주",
    subtitle: "밤늦게까지, 안주 한 잔",
    emoji: "🌙",
  },
  {
    slug: "rainy-day",
    href: "/topics/rainy-day",
    title: "비 오는 날 추천",
    subtitle: "따뜻한 국물·실내에서 편하게",
    emoji: "🌧️",
  },
  {
    slug: "hot-weather",
    href: "/topics/hot-weather",
    title: "더운 날씨 맛집",
    subtitle: "시원·가벼운 메뉴로 더위 날리기",
    emoji: "☀️",
  },
  {
    slug: "hangover-cure",
    href: "/topics/hangover-cure",
    title: "해장 맛집",
    subtitle: "숙취에도 든든한 국물·콩나물 한 그릇",
    emoji: "🍲",
  },
  {
    slug: "cold-weather",
    href: "/topics/cold-weather",
    title: "추운 날씨 맛집",
    subtitle: "든든한 한 끼로 몸 녹이기",
    emoji: "❄️",
  },
  {
    slug: "solo-dining",
    href: "/topics/solo-dining",
    title: "혼밥하기 좋은",
    subtitle: "혼자 와도 부담 없는 자리",
    emoji: "🧑",
  },
  {
    slug: "group-dining",
    href: "/topics/group-dining",
    title: "단체·회식",
    subtitle: "여럿이 모이기 좋은 넓은 테이블",
    emoji: "👥",
  },
  {
    slug: "instagram-worthy",
    href: "/topics/instagram-worthy",
    title: "인스타 감성",
    subtitle: "사진 찍기 좋은 인테리어·플레이팅",
    emoji: "📸",
  },
  {
    slug: "locals-favorite",
    href: "/topics/locals-favorite",
    title: "현지인 단골",
    subtitle: "동네 주민이 줄 서는 곳",
    emoji: "📍",
  },
  {
    slug: "tourist-friendly",
    href: "/topics/tourist-friendly",
    title: "관광객 추천",
    subtitle: "서울 여행 중 꼭 가볼 만한",
    emoji: "🧳",
  },
  {
    slug: "open-late",
    href: "/topics/open-late",
    title: "늦게까지 영업",
    subtitle: "야근·야행 후에도 OK",
    emoji: "🕐",
  },
  {
    slug: "lunch-special",
    href: "/topics/lunch-special",
    title: "점심 특선",
    subtitle: "런치 메뉴·세트가 알찬 곳",
    emoji: "🍱",
  },
  {
    slug: "near-station",
    href: "/topics/near-station",
    title: "역세권·도보 5분",
    subtitle: "대중교통으로 바로",
    emoji: "🚇",
  },
  {
    slug: "trending-now",
    href: "/topics/trending-now",
    title: "지금 뜨는 곳",
    subtitle: "최근 조회·관심 급상승",
    emoji: "🔥",
  },
];

export function getTopicBySlug(slug: string): GourmetTopic | undefined {
  return HOME_TOPIC_LINKS.find((t) => t.slug === slug);
}
