"""업종·라벨 문자열 → 표준 ``category_slug`` / ``category_label``."""

from __future__ import annotations

# 식사 위주 추천에서 제외 (카페·디저트·주점·바)
NON_MEAL_CATEGORY_SLUGS: frozenset[str] = frozenset({"cafe-dessert", "bar"})


def is_meal_category_slug(slug: str | None) -> bool:
    """True면 일일 맛집 추천 풀에 포함 가능."""
    if not slug:
        return True
    return slug not in NON_MEAL_CATEGORY_SLUGS


def classify_sgma_category(
    biz_mid_name: str, biz_minor_name: str, ksic_name: str
) -> tuple[str, str]:
    """상권 업종 문자열을 앱 ``category_slug``·라벨로 매핑."""
    text = f"{biz_mid_name} {biz_minor_name} {ksic_name}"

    def has(*keys: str) -> bool:
        return any(k in text for k in keys)

    if has("카페", "커피", "디저트", "베이커리", "제과", "빵"):
        return "cafe-dessert", "카페·디저트"
    if has("주점", "요리 주점", "호프"):
        return "bar", "바"
    if has("일식", "스시", "사시미", "라멘", "돈까스", "돈카츠", "우동", "초밥", "오코노미"):
        return "ilsik", "일식"
    if has("중식", "중화", "중국", "짜장", "짬뽕", "마라", "딤섬", "양꼬치"):
        return "jungsik", "중식"
    if has("양식", "파스타", "피자", "스테이크", "버거", "패스트푸드", "패밀리"):
        return "yangsik", "양식"
    if has("태국", "베트남", "태국식", "쌀국수", "포 ", "반미", "인도", "멕시코", "타코"):
        return "asian", "아시안"
    if has("분식", "떡볶이", "김밥", "어묵"):
        return "bunsik", "분식"
    return "hansik", "한식"


class CategoryNormalizer:
    """'대한음식', '한국요리' 등 별칭을 통합한 뒤 slug·라벨을 반환."""

    _LABEL_ALIASES: dict[str, str] = {
        "대한음식": "한식",
        "한국요리": "한식",
        "한국식": "한식",
        "korean": "한식",
        "중국요리": "중식",
        "중화요리": "중식",
        "일본요리": "일식",
        "일본식": "일식",
        "서양식": "양식",
        "western": "양식",
        "카페": "카페·디저트",
        "커피": "카페·디저트",
    }

    _SLUG_BY_LABEL: dict[str, tuple[str, str]] = {
        "한식": ("hansik", "한식"),
        "일식": ("ilsik", "일식"),
        "중식": ("jungsik", "중식"),
        "양식": ("yangsik", "양식"),
        "아시안": ("asian", "아시안"),
        "분식": ("bunsik", "분식"),
        "카페·디저트": ("cafe-dessert", "카페·디저트"),
        "바": ("bar", "바"),
    }

    def normalize_label(self, raw_label: str) -> str:
        t = (raw_label or "").strip()
        if not t:
            return ""
        for alias, canonical in self._LABEL_ALIASES.items():
            if alias in t or t == alias:
                return canonical
        return t

    def from_biz_fields(
        self, biz_mid_name: str, biz_minor_name: str, ksic_name: str
    ) -> tuple[str, str]:
        """공공데이터 업종 3필드 → (category_slug, category_label)."""
        combined = f"{biz_mid_name} {biz_minor_name} {ksic_name}"
        for alias, canonical in self._LABEL_ALIASES.items():
            if alias in combined:
                combined = combined.replace(alias, canonical)
        slug, label = classify_sgma_category(biz_mid_name, biz_minor_name, ksic_name)
        label = self.normalize_label(label) or label
        if label in self._SLUG_BY_LABEL:
            return self._SLUG_BY_LABEL[label]
        return slug, label
