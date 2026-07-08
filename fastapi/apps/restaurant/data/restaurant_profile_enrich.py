"""식당 상세 프로필(메뉴·주소·연락처) 생성·보강."""

from __future__ import annotations

import hashlib
import re
from typing import Any

# 카테고리별 기본 메뉴 (이름, 가격원, 비고)
DEFAULT_MENUS: dict[str, list[dict[str, Any]]] = {
    "hansik": [
        {"name": "한정식 코스 A", "price": 28000, "note": "제철 나물 7종"},
        {"name": "된장찌개 정식", "price": 12000, "note": ""},
        {"name": "삼겹살 2인 세트", "price": 36000, "note": "상추·쌈장 포함"},
        {"name": "비빔밥", "price": 11000, "note": ""},
        {"name": "막걸리", "price": 4000, "note": "전통주"},
    ],
    "ilsik": [
        {"name": "돈코츠 라멘", "price": 12000, "note": "시그니처"},
        {"name": "미소 라멘", "price": 11000, "note": ""},
        {"name": "돈카츠 정식", "price": 13000, "note": "밥·국 포함"},
        {"name": "모듬 사시미", "price": 35000, "note": "2인 기준"},
        {"name": "하이볼", "price": 7000, "note": ""},
    ],
    "jungsik": [
        {"name": "짜장면", "price": 8000, "note": ""},
        {"name": "짬뽕", "price": 9000, "note": ""},
        {"name": "탕수육(小)", "price": 18000, "note": ""},
        {"name": "군만두", "price": 7000, "note": ""},
        {"name": "마라탕", "price": 14000, "note": "매운맛 단계 선택"},
    ],
    "yangsik": [
        {"name": "트러플 크림 파스타", "price": 18000, "note": ""},
        {"name": "마르게리타 피자", "price": 16000, "note": ""},
        {"name": "스테이크 200g", "price": 42000, "note": "미디엄 기본"},
        {"name": "브런치 플레이트", "price": 22000, "note": "주말 한정"},
        {"name": "하우스 와인", "price": 9000, "note": "글라스"},
    ],
    "asian": [
        {"name": "쌀국수", "price": 11000, "note": ""},
        {"name": "반미", "price": 9500, "note": ""},
        {"name": "팟타이", "price": 13000, "note": ""},
        {"name": "버터 치킨", "price": 15000, "note": "난 포함"},
        {"name": "땀망", "price": 6000, "note": ""},
    ],
    "bunsik": [
        {"name": "떡볶이", "price": 5500, "note": ""},
        {"name": "김밥", "price": 4000, "note": ""},
        {"name": "라면", "price": 5000, "note": ""},
        {"name": "튀김 모듬", "price": 7000, "note": ""},
        {"name": "순대", "price": 6000, "note": ""},
    ],
    "cafe-dessert": [
        {"name": "아메리카노", "price": 4500, "note": ""},
        {"name": "카페라떼", "price": 5500, "note": ""},
        {"name": "크루아상", "price": 4500, "note": ""},
        {"name": "치즈케이크", "price": 7500, "note": ""},
        {"name": "아포가토", "price": 6800, "note": ""},
    ],
    "bar": [
        {"name": "시그니처 칵테일", "price": 15000, "note": ""},
        {"name": "생맥주", "price": 6000, "note": ""},
        {"name": "안주 모듬", "price": 28000, "note": "2~3인"},
        {"name": "하이볼", "price": 8000, "note": ""},
        {"name": "와인 글라스", "price": 10000, "note": ""},
    ],
}

DISTRICT_GU: dict[str, str] = {
    "종로": "종로구",
    "중구": "중구",
    "마포": "마포구",
    "용산": "용산구",
    "강남": "강남구",
    "서대문": "서대문구",
    "성동": "성동구",
    "영등포": "영등포구",
    "송파": "송파구",
    "광진": "광진구",
    "동작": "동작구",
    "성북": "성북구",
    "노원": "노원구",
    "청담": "강남구",
    "한남": "용산구",
    "압구정": "강남구",
    "이태원": "용산구",
    "연남": "마포구",
    "건대": "광진구",
    "홍대": "마포구",
    "을지로": "중구",
    "망원": "마포구",
    "성수": "성동구",
    "여의도": "영등포구",
    "대림": "영등포구",
}

# 매장별 맞춤 데이터
PROFILE_OVERRIDES: dict[str, dict[str, Any]] = {
    "홍대 라멘야": {
        "address": "서울특별시 마포구 어울마당로 130-12, 1층",
        "opening_hours": "매일 11:30 - 23:00 (라스트오더 22:30)",
        "phone": "02-334-7821",
        "instagram_url": "https://www.instagram.com/",
        "reservation_available": True,
        "reservation_note": "전화 예약 · 당일 방문 가능 (Instagram DM 문의)",
        "menu_items": [
            {"name": "돈코츠 라멘", "price": 12000, "note": "시그니처 · 진한 돈골 국물"},
            {"name": "미소 라멘", "price": 11000, "note": ""},
            {"name": "매운 돈코츠", "price": 13000, "note": "카라메 2단계"},
            {"name": "차슈멘", "price": 14000, "note": "차슈 추가"},
            {"name": "교자 5pcs", "price": 6000, "note": "사이드"},
            {"name": "하이볼", "price": 7000, "note": ""},
        ],
    },
}


def _seed_int(name: str) -> int:
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)


def _slug_handle(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9가-힣]", "", name).lower()[:20]
    return s or "gourmetmate"


def build_profile(name: str, district: str, category_slug: str) -> dict[str, Any]:
    if name in PROFILE_OVERRIDES:
        return dict(PROFILE_OVERRIDES[name])

    h = _seed_int(name)
    gu = DISTRICT_GU.get(district, f"{district}구")
    street_no = 10 + (h % 200)
    sub = (h % 50) + 1
    address = f"서울특별시 {gu} {district}로{street_no}길 {sub}"

    weekday_open = 11 + (h % 2)
    weekday_close = 21 + (h % 3)
    weekend_close = 22 + (h % 2)
    opening_hours = (
        f"평일 {weekday_open}:00 - {weekday_close}:00 · "
        f"주말 {weekday_open}:30 - {weekend_close}:30"
    )

    phone = f"02-{(2000 + h % 7000):04d}-{(1000 + (h // 7) % 8000):04d}"
    instagram_url = f"https://www.instagram.com/"
    reservation_available = (h % 3) != 0
    reservation_note = (
        "전화 예약 가능 · Instagram DM 문의"
        if reservation_available
        else "워크인 환영 (예약 불필요)"
    )

    menus = DEFAULT_MENUS.get(category_slug, DEFAULT_MENUS["hansik"])
  # slight price variation per store
    menu_items = []
    for i, m in enumerate(menus):
        offset = (h % 5) * 500 if i == 0 else 0
        menu_items.append(
            {
                "name": m["name"],
                "price": m["price"] + offset,
                "note": m.get("note", ""),
            }
        )

    return {
        "address": address,
        "opening_hours": opening_hours,
        "phone": phone,
        "instagram_url": instagram_url,
        "reservation_available": reservation_available,
        "reservation_note": reservation_note,
        "menu_items": menu_items,
    }


def enrich_seed_row(row: dict[str, Any]) -> dict[str, Any]:
    profile = build_profile(
        row["name"], row.get("district", ""), row.get("category_slug", "hansik")
    )
    out = {**row}
    for key, val in profile.items():
        out.setdefault(key, val)
    from restaurant.data.restaurant_images import apply_image_to_seed_row

    return apply_image_to_seed_row(out)
