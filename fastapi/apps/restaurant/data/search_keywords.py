"""검색어 확장 — 주제·메뉴·설명 매칭용 동의어."""

from __future__ import annotations

# 검색어(또는 부분 일치) → 관련 키워드
SEARCH_EXPANSIONS: dict[str, tuple[str, ...]] = {
    "여름": ("여름", "냉면", "빙수", "시원", "냉모밀", "콩국수", "냉국수", "수박", "샐러드", "가벼운"),
    "겨울": ("겨울", "추위", "찌개", "전골", "곰탕", "설렁탕", "따뜻", "든든", "탕"),
    "해장": ("해장", "숙취", "국밥", "뼈해장", "콩나물", "우거지", "해장국", "얼큰", "라면"),
    "비": ("비", "장마", "우중", "국물", "전골", "실내"),
    "데이트": ("데이트", "커플", "로맨틱", "기념일", "연인", "분위기"),
    "혼밥": ("혼밥", "혼자", "1인", "솔로"),
    "야식": ("야식", "야장", "늦은", "심야", "안주", "포차"),
    "가성비": ("가성비", "저렴", "합리적", "알뜰", "착한가격"),
    "브런치": ("브런치", "주말", "아침", "에그"),
    "매운": ("매운", "맵", "마라", "얼큰", "고추"),
    "국물": ("국물", "탕", "찌개", "전골", "라면"),
    "디저트": ("디저트", "케이크", "달콤", "아이스크림", "빵"),
    "커피": ("커피", "카페", "라떼", "드립", "에스프레소"),
    "회": ("회", "사시미", "스시", "오마카세", "횟집"),
    "고기": ("고기", "구이", "삼겹", "갈비", "스테이크"),
}

# 검색어 → 우선 매칭할 주제 slug
QUERY_TOPIC_SLUGS: dict[str, tuple[str, ...]] = {
    "여름": ("hot-weather",),
    "겨울": ("cold-weather",),
    "해장": ("hangover-cure", "soup-stew"),
    "비": ("rainy-day",),
    "데이트": ("date-spots",),
    "혼밥": ("solo-dining",),
    "야식": ("late-night-bites",),
    "가성비": ("value-picks",),
}


def expand_search_terms(q: str) -> list[str]:
    """입력을 소문자 키워드 목록으로 확장."""
    raw = q.strip().lower()
    if not raw:
        return []
    terms: set[str] = {raw}
    for key, extras in SEARCH_EXPANSIONS.items():
        key_l = key.lower()
        matched = key_l in raw or raw in key_l
        if not matched:
            for extra in extras:
                el = extra.lower()
                if el in raw or raw in el:
                    matched = True
                    break
        if matched:
            terms.add(key_l)
            terms.update(e.lower() for e in extras)
    return list(terms)


def topic_slugs_for_query(q: str, terms: list[str] | None = None) -> tuple[str, ...]:
    """검색어에 연결된 주제 slug."""
    raw = q.strip().lower()
    needles = set(terms or expand_search_terms(q))
    slugs: list[str] = []
    for key, topic_slugs in QUERY_TOPIC_SLUGS.items():
        if key in raw or raw in key or key in needles:
            slugs.extend(topic_slugs)
    return tuple(dict.fromkeys(slugs))
