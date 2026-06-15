"""카테고리별 맛집 주제(넷플릭스 행) 정의."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopicDef:
    slug: str
    title: str
    subtitle: str
    emoji: str
    keywords: tuple[str, ...]
    """비어 있으면 모든 카테고리에 노출."""
    category_slugs: tuple[str, ...] = ()


# 모든 음식 장르에 공통
COMMON_TOPICS: tuple[TopicDef, ...] = (
    TopicDef(
        "value-picks",
        "가성비 맛집",
        "부담 없이 즐기는 가격 대비 만족도",
        "💰",
        ("가성비", "저렴", "합리적", "가격", "알뜰", "착한가격"),
    ),
    TopicDef(
        "date-spots",
        "데이트 명소",
        "분위기와 서비스가 좋은 로맨틱 스팟",
        "💑",
        ("데이트", "커플", "로맨틱", "기념일", "연인"),
    ),
    TopicDef(
        "late-night-bites",
        "야장·술안주",
        "밤늦게까지, 안주 한 잔",
        "🌙",
        ("야장", "야식", "술집", "안주", "밤", "늦은", "포차"),
    ),
    TopicDef(
        "rainy-day",
        "비 오는 날 추천",
        "따뜻한 국물·실내에서 편하게",
        "🌧️",
        ("비", "장마", "우중", "국물", "실내"),
    ),
    TopicDef(
        "hot-weather",
        "더운 날씨 맛집",
        "시원·가벼운 메뉴로 더위 날리기",
        "☀️",
        ("더위", "여름", "시원", "냉면", "샐러드", "가벼운"),
    ),
    TopicDef(
        "hangover-cure",
        "해장 맛집",
        "숙취에도 든든한 국물·콩나물 한 그릇",
        "🍲",
        ("해장", "숙취", "국밥", "뼈해장", "콩나물", "우거지", "해장국", "얼큰"),
    ),
    TopicDef(
        "cold-weather",
        "추운 날씨 맛집",
        "든든한 한 끼로 몸 녹이기",
        "❄️",
        ("추위", "겨울", "따뜻", "든든", "찌개", "탕"),
    ),
    TopicDef(
        "solo-dining",
        "혼밥하기 좋은",
        "혼자 와도 부담 없는 자리",
        "🧑",
        ("혼밥", "혼자", "1인", "솔로"),
    ),
    TopicDef(
        "group-dining",
        "단체·회식",
        "여럿이 모이기 좋은 넓은 테이블",
        "👥",
        ("단체", "회식", "모임", "가족", "여럿"),
    ),
    TopicDef(
        "instagram-worthy",
        "인스타 감성",
        "사진 찍기 좋은 인테리어·플레이팅",
        "📸",
        ("인스타", "감성", "사진", "예쁜", "플레이팅"),
    ),
    TopicDef(
        "locals-favorite",
        "현지인 단골",
        "동네 주민이 줄 서는 곳",
        "📍",
        ("현지인", "단골", "동네", "로컬", "숨은"),
    ),
    TopicDef(
        "tourist-friendly",
        "관광객 추천",
        "서울 여행 중 꼭 가볼 만한",
        "🧳",
        ("관광", "여행", "외국인", "명소", "서울"),
    ),
    TopicDef(
        "open-late",
        "늦게까지 영업",
        "야근·야행 후에도 OK",
        "🕐",
        ("늦게", "심야", "24", "야간", "영업"),
    ),
    TopicDef(
        "lunch-special",
        "점심 특선",
        "런치 메뉴·세트가 알찬 곳",
        "🍱",
        ("점심", "런치", "런치세트", "낮"),
    ),
    TopicDef(
        "near-station",
        "역세권·도보 5분",
        "대중교통으로 바로",
        "🚇",
        ("역세권", "역", "도보", "교통", "가까운"),
    ),
    TopicDef(
        "quiet-vibe",
        "조용한 분위기",
        "대화에 집중하기 좋은",
        "🤫",
        ("조용", "한적", "프라이빗", "차분"),
    ),
    TopicDef(
        "lively-vibe",
        "활기찬 분위기",
        "에너지 넘치는 식당",
        "🎉",
        ("활기", "시끌", "분위기", "파티", "북적"),
    ),
    TopicDef(
        "night-view",
        "전망·야경",
        "창밖 풍경이 있는 곳",
        "🌃",
        ("야경", "전망", "루프탑", "뷰", "창가"),
    ),
    TopicDef(
        "family-friendly",
        "가족 외식",
        "아이·부모님과 함께",
        "👨‍👩‍👧",
        ("가족", "아이", "부모님", "키즈"),
    ),
    TopicDef(
        "walk-in",
        "예약 없이 방문",
        "워크인 환영",
        "🚶",
        ("워크인", "예약없이", "바로", "대기"),
    ),
    TopicDef(
        "trending-now",
        "지금 뜨는 곳",
        "최근 조회·관심 급상승",
        "🔥",
        ("인기", "핫", "트렌드", "뜨는", "화제"),
    ),
    TopicDef(
        "spicy-lovers",
        "매운맛 좋아한다면",
        "얼큰·매콤한 메뉴가 있는 곳",
        "🌶️",
        ("매운", "얼큰", "고추", "청양", "마라", "핫"),
    ),
    TopicDef(
        "comfort-food",
        "편안한 한 끼",
        "부담 없이 자주 찾게 되는 맛",
        "🍚",
        ("편안", "집밥", "든든", "한그릇", "정갈"),
    ),
    TopicDef(
        "weekend-special",
        "주말 외식",
        "토·일에 여유 있게 즐기기",
        "📅",
        ("주말", "토요일", "일요일", "브런치", "외식"),
    ),
    TopicDef(
        "anniversary",
        "기념일·생일",
        "특별한 날 분위기",
        "🎂",
        ("기념일", "생일", "축하", "케이크", "이벤트"),
    ),
    TopicDef(
        "quick-bite",
        "빠른 한 끼",
        "점심시간·이동 중 가볍게",
        "⚡",
        ("빠른", "간편", "테이크아웃", "포장", "도시락"),
    ),
    TopicDef(
        "soup-lovers",
        "국물 요리",
        "탕·찌개·전골 한 그릇",
        "🥣",
        ("국물", "탕", "찌개", "전골", "국밥", "곰탕"),
    ),
    TopicDef(
        "noodle-craving",
        "면 요리",
        "국수·라면·냉면·파스타",
        "🍜",
        ("면", "국수", "라면", "냉면", "우동", "파스타"),
    ),
    TopicDef(
        "rice-bowl",
        "밥 한 공기",
        "덮밥·비빔·정식",
        "🍚",
        ("밥", "덮밥", "비빔밥", "정식", "볶음밥"),
    ),
    TopicDef(
        "seafood-fresh",
        "해산물·회",
        "싱싱한 해산물 메뉴",
        "🦐",
        ("해산물", "회", "생선", "조개", "새우", "게"),
    ),
    TopicDef(
        "fried-crispy",
        "바삭·튀김",
        "튀김·전·바삭한 식감",
        "🍤",
        ("튀김", "바삭", "전", "치킨", "돈까스", "크림새우"),
    ),
    TopicDef(
        "healthy-light",
        "가볍게 먹기",
        "샐러드·저염·담백",
        "🥗",
        ("샐러드", "가볍", "담백", "건강", "다이어트"),
    ),
    TopicDef(
        "business-meal",
        "비즈니스 미팅",
        "조용히 대화하기 좋은",
        "💼",
        ("미팅", "비즈니스", "상견례", "접대"),
    ),
    TopicDef(
        "student-budget",
        "학생·알뜰",
        "부담 없는 가격대",
        "🎓",
        ("학생", "알뜰", "저렴", "학교", "대학"),
    ),
    TopicDef(
        "late-breakfast",
        "브런치·늦은 아침",
        "주말 아침부터 여유롭게",
        "🥞",
        ("브런치", "아침", "에그", "팬케이크", "오믈렛"),
    ),
    TopicDef(
        "takeout-friendly",
        "포장·배달 잘하는",
        "집에서도 맛있게",
        "🥡",
        ("포장", "배달", "테이크아웃", "도시락"),
    ),
    TopicDef(
        "hidden-gem",
        "숨은 맛집",
        "유명세 없이 실력 있는 곳",
        "💎",
        ("숨은", "소문", "로컬", "동네", "오래"),
    ),
    TopicDef(
        "chefs-pick",
        "셰프·전문점",
        "한 메뉴에 진심인 곳",
        "👨‍🍳",
        ("전문", "본점", "원조", "명인", "장인"),
    ),
)

# 메인 홈 피드 — 식사 장르 주제만 (카페·주점 제외)
HOME_FEED_CATEGORY_SLUGS: tuple[str, ...] = (
    "hansik",
    "ilsik",
    "jungsik",
    "yangsik",
    "asian",
    "bunsik",
)

# 장르별 추가 주제
CATEGORY_EXTRA_TOPICS: dict[str, tuple[TopicDef, ...]] = {
    "hansik": (
        TopicDef(
            "hanjeongsik",
            "한정식·코스",
            "제철 나물과 정갈한 상차림",
            "🍱",
            ("한정식", "코스", "상차림", "나물"),
            ("hansik",),
        ),
        TopicDef(
            "bbq-grill",
            "고기·구이",
            "직화·삼겹·갈비",
            "🥩",
            ("구이", "고기", "삼겹", "갈비", "직화"),
            ("hansik",),
        ),
        TopicDef(
            "soup-stew",
            "국물·찌개",
            "얼큰·시원한 국물 한 그릇",
            "🍲",
            ("찌개", "국물", "탕", "전골"),
            ("hansik",),
        ),
        TopicDef(
            "pojang-vibe",
            "포장마차 감성",
            "골목·노포 분위기",
            "🏮",
            ("포차", "골목", "노포", "을지로"),
            ("hansik",),
        ),
    ),
    "ilsik": (
        TopicDef(
            "omakase",
            "오마카세",
            "셰프 추천 코스",
            "🍣",
            ("오마카세", "스시", "코스"),
            ("ilsik",),
        ),
        TopicDef(
            "ramen",
            "라멘 전문",
            "진한 국물과 쫄깃한 면",
            "🍜",
            ("라멘", "면", "돈코츠"),
            ("ilsik",),
        ),
        TopicDef(
            "izakaya",
            "이자카야",
            "사케·안주 한 잔",
            "🍶",
            ("이자카야", "사케", "안주"),
            ("ilsik",),
        ),
    ),
    "jungsik": (
        TopicDef(
            "dimsum",
            "딤섬·중식 디저트",
            "샤오롱바오·군만",
            "🥟",
            ("딤섬", "만두", "군만"),
            ("jungsik",),
        ),
        TopicDef(
            "spicy-mala",
            "마라·얼큰",
            "훠궈·마라탕",
            "🌶️",
            ("마라", "훠궈", "매운", "얼큰"),
            ("jungsik",),
        ),
    ),
    "yangsik": (
        TopicDef(
            "pasta",
            "파스타",
            "이탈리안 면 요리",
            "🍝",
            ("파스타", "이탈리안", "면"),
            ("yangsik",),
        ),
        TopicDef(
            "steak",
            "스테이크·그릴",
            "프리미엄 육류",
            "🥩",
            ("스테이크", "그릴", "육류"),
            ("yangsik",),
        ),
        TopicDef(
            "brunch",
            "브런치",
            "늦은 아침·주말",
            "🥐",
            ("브런치", "주말", "아침"),
            ("yangsik",),
        ),
        TopicDef(
            "wine-pairing",
            "와인 페어링",
            "와인과 어울리는 코스",
            "🍷",
            ("와인", "페어링", "바"),
            ("yangsik",),
        ),
    ),
    "asian": (
        TopicDef(
            "thai",
            "태국·쏨땀",
            "새콤·매콤한 향신",
            "🇹🇭",
            ("태국", "쏨땀", "팟타이"),
            ("asian",),
        ),
        TopicDef(
            "vietnamese",
            "베트남·쌀국수",
            "담백한 국물",
            "🇻🇳",
            ("베트남", "쌀국수", "반미"),
            ("asian",),
        ),
        TopicDef(
            "indian",
            "인도·커리",
            "향신 가득",
            "🇮🇳",
            ("인도", "커리", "난"),
            ("asian",),
        ),
    ),
    "bunsik": (
        TopicDef(
            "tteokbokki",
            "떡볶이·분식",
            "매콤달콤 스트리트 푸드",
            "🌶️",
            ("떡볶이", "분식", "김밥"),
            ("bunsik",),
        ),
        TopicDef(
            "street-food",
            "길거리 간식",
            "포장·테이크아웃",
            "🥡",
            ("길거리", "포장", "테이크아웃"),
            ("bunsik",),
        ),
    ),
    "cafe-dessert": (
        TopicDef(
            "specialty-coffee",
            "스페셜티 커피",
            "로스팅·핸드드립",
            "☕",
            ("커피", "스페셜티", "드립", "로스팅"),
            ("cafe-dessert",),
        ),
        TopicDef(
            "bakery",
            "베이커리",
            "빵·페이스트리",
            "🥐",
            ("베이커리", "빵", "디저트", "케이크"),
            ("cafe-dessert",),
        ),
        TopicDef(
            "dessert-cafe",
            "디저트 카페",
            "케이크·아이스크림",
            "🍰",
            ("디저트", "케이크", "아이스크림", "달콤"),
            ("cafe-dessert",),
        ),
    ),
    "bar": (
        TopicDef(
            "cocktail-bar",
            "칵테일 바",
            "시그니처 칵테일",
            "🍸",
            ("칵테일", "바", "믹솔로지"),
            ("bar",),
        ),
        TopicDef(
            "wine-bar",
            "와인 바",
            "글라스·보틀",
            "🍷",
            ("와인바", "와인", "내추럴"),
            ("bar",),
        ),
        TopicDef(
            "pocha",
            "포차·주점",
            "안주와 소주 한 잔",
            "🍺",
            ("포차", "소주", "맥주", "주점"),
            ("bar",),
        ),
    ),
}


ALL_CATEGORY_SLUGS: frozenset[str] = frozenset(
    {
        "hansik",
        "ilsik",
        "jungsik",
        "yangsik",
        "asian",
        "bunsik",
        "cafe-dessert",
        "bar",
    }
)


def all_topic_defs() -> list[TopicDef]:
    """전체 주제(중복 slug 제거) — API 카탈로그·주제 상세용."""
    seen: set[str] = set()
    ordered: list[TopicDef] = []
    for t in COMMON_TOPICS:
        if t.slug in seen:
            continue
        seen.add(t.slug)
        ordered.append(t)
    for slug in ALL_CATEGORY_SLUGS:
        for t in CATEGORY_EXTRA_TOPICS.get(slug, ()):
            if t.slug in seen:
                continue
            seen.add(t.slug)
            ordered.append(t)
    return ordered


def find_topic_by_slug(slug: str) -> TopicDef | None:
    key = (slug or "").strip()
    if not key:
        return None
    for t in all_topic_defs():
        if t.slug == key:
            return t
    return None


def topics_for_category(category_slug: str) -> list[TopicDef]:
    """공통 + 해당 장르 전용 주제."""
    extras = CATEGORY_EXTRA_TOPICS.get(category_slug, ())
    return list(COMMON_TOPICS) + list(extras)


def home_feed_topics(q: str | None = None) -> list[TopicDef]:
    """메인 홈 무한 스크롤 — 공통 주제 전체 + 식사 장르 전용 주제."""
    seen: set[str] = set()
    ordered: list[TopicDef] = []
    for t in COMMON_TOPICS:
        if t.slug in seen:
            continue
        seen.add(t.slug)
        ordered.append(t)
    for slug in HOME_FEED_CATEGORY_SLUGS:
        for t in CATEGORY_EXTRA_TOPICS.get(slug, ()):
            if t.slug in seen:
                continue
            seen.add(t.slug)
            ordered.append(t)
    if q and q.strip():
        return filter_topics_by_query(ordered, q)
    return ordered


def filter_topics_by_query(topics: list[TopicDef], q: str) -> list[TopicDef]:
    from restaurant.data.search_keywords import expand_search_terms

    terms = expand_search_terms(q)
    if not terms:
        return topics
    out: list[TopicDef] = []
    for t in topics:
        hay = " ".join(
            [t.title, t.subtitle, t.slug, " ".join(t.keywords)]
        ).lower()
        if any(term in hay for term in terms):
            out.append(t)
    return out
