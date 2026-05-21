"""업종·라벨 문자열 → 표준 ``category_slug`` / ``category_label``."""

from __future__ import annotations

from apps.gourmet.app.services.sgma_restaurant_service import classify_sgma_category


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
