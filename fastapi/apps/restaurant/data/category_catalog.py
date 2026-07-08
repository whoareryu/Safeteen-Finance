"""앱 표준 음식 장르 slug ↔ 라벨 (DB ``food_categories`` 시드와 동일)."""

CATEGORY_LABEL_BY_SLUG: dict[str, str] = {
    "hansik": "한식",
    "ilsik": "일식",
    "jungsik": "중식",
    "yangsik": "양식",
    "asian": "아시안",
    "bunsik": "분식",
    "cafe-dessert": "카페·디저트",
    "bar": "바",
}
