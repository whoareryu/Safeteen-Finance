"""매장별 대표 이미지 — 장르·메뉴·설명 키워드 매칭."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FoodImage:
    url: str
    tags: tuple[str, ...]


def _u(photo_id: str) -> str:
    return f"https://images.unsplash.com/photo-{photo_id}?w=800&q=85&fit=crop"


# 장르별 음식·매장 분위기 사진 풀 (메뉴/플레이팅·테이블)
CATEGORY_IMAGE_POOLS: dict[str, tuple[FoodImage, ...]] = {
    "hansik": (
        FoodImage(_u("1590301157897-05f3a3da5ab4"), ("한정식", "나물", "상차림", "코스")),
        FoodImage(_u("1604908177525-6831cbab1f1c"), ("국물", "탕", "설렁탕", "곰탕", "국밥")),
        FoodImage(_u("1547592166-23ac45744acd"), ("찌개", "얼큰", "동태", "전골", "국물")),
        FoodImage(_u("1529042410759-befb1204b916"), ("삼겹", "구이", "고기", "솥뚜껑", "갈비")),
        FoodImage(_u("1544025162-d76694265947"), ("갈비", "양념", "고기", "구이")),
        FoodImage(_u("1625938145744-e38051536038"), ("보쌈", "수육", "한상", "정식")),
        FoodImage(_u("1553163147-622ab57be1c7"), ("한식", "밑반찬", "집밥", "노포")),
        FoodImage(_u("1606728035253-49e8a23146de"), ("구이", "직화", "고기")),
        FoodImage(_u("1604908176997-125f25cc6f3d"), ("찌개", "된장", "찌개")),
        FoodImage(_u("1546833999-b9f581a1996d"), ("비빔밥", "밥", "채소")),
        FoodImage(_u("1498654896293-37aec7881f44"), ("한식", "전통")),
        FoodImage(_u("1600891964092-4316c288032e"), ("회", "매운탕", "해산물", "노량진")),
    ),
    "ilsik": (
        FoodImage(_u("1569718212165-3a8278d5f624"), ("라멘", "면", "돈코츠", "국물")),
        FoodImage(_u("1579584425555-c3ce17fd1871"), ("스시", "사시미", "오마카세", "네타")),
        FoodImage(_u("1623855248186-52f656884a59"), ("돈카츠", "튀김", "정식")),
        FoodImage(_u("1617196034791-47de43f660e4"), ("이자카야", "꼬치", "야키토리", "안주")),
        FoodImage(_u("1553621042-f6e147245754"), ("스시", "초밥", "회")),
        FoodImage(_u("1618841557871-569f316a0e3a"), ("우동", "면")),
        FoodImage(_u("1557878981-814165de8f72"), ("오코노미", "철판", "야키소바")),
        FoodImage(_u("1580822183893-049bb9a8e295"), ("텐동", "튀김", "덮밥")),
        FoodImage(_u("1617092621-0b2e46b1d09e"), ("이자카야", "하이볼", "술")),
        FoodImage(_u("1617196034791-47de43f660e4"), ("일식", "정식", "백반")),
    ),
    "jungsik": (
        FoodImage(_u("1525755662778-989d3524086e"), ("짜장", "짬뽕", "중식", "면")),
        FoodImage(_u("1582878826629-29ae1f063f83"), ("딤섬", "군만", "하가우", "샤오롱")),
        FoodImage(_u("1496116218417-69778153be98"), ("만두", "딤섬")),
        FoodImage(_u("1585030013374-00a1dde83f9c"), ("훠궈", "전골", "탕")),
        FoodImage(_u("1563379091339-ee6e7e6c3e5a"), ("마라", "마라탕", "얼얼", "매운")),
        FoodImage(_u("1526318472351-cad71565b2c6"), ("탕수육", "유린기", "볶음")),
        FoodImage(_u("1585030013374-00a1dde83f9c"), ("중화", "볶음밥")),
        FoodImage(_u("1563245372-f21724e3856d"), ("양꼬치", "꼬치", "안주")),
    ),
    "yangsik": (
        FoodImage(_u("1476124369491-e7addf5ef851"), ("브런치", "에그", "아침")),
        FoodImage(_u("1565299624946-b28f40a0ae38"), ("파스타", "면", "이탈리안")),
        FoodImage(_u("1513104890138-7c749659a592"), ("피자", "화덕", "치즈")),
        FoodImage(_u("1546069901-ba9599a7e63c"), ("스테이크", "고기", "그릴")),
        FoodImage(_u("1568901346375-23c9450c58cd"), ("버거", "패티")),
        FoodImage(_u("1473093295048-9db8a9a774b2"), ("파스타", "생면", "공방")),
        FoodImage(_u("1414235077428-338989a2e8c0"), ("비스트로", "코스", "양식")),
        FoodImage(_u("1540189546936-380986bb09c8"), ("리조또", "크림", "버섯")),
    ),
    "asian": (
        FoodImage(_u("1559314809-0d155014e29e"), ("팟타이", "태국", "쏨땀", "면")),
        FoodImage(_u("1582878826629-29ae1f063f83"), ("쌀국수", "베트남", "포", "반미")),
        FoodImage(_u("1585937421612-70a008296fbe"), ("커리", "인도", "난", "탄두리")),
        FoodImage(_u("1565299585323-38d6b0865b47"), ("타코", "멕시칸", "부리토")),
        FoodImage(_u("1555939594-58d7cb561ad1"), ("해산물", "칠리", "크랩")),
        FoodImage(_u("1544025162-d76694265947"), ("아시안", "향신")),
    ),
    "bunsik": (
        FoodImage(_u("1589314276789-4caa0cbc9c0b"), ("떡볶이", "매콤", "분식")),
        FoodImage(_u("1582878826629-29ae1f063f83"), ("김밥", "분식", "간편")),
        FoodImage(_u("1569718212165-3a8278d5f624"), ("라면", "야식", "만두")),
        FoodImage(_u("1604908176997-125f25cc6f3d"), ("곱창", "구이", "대창")),
        FoodImage(_u("1568901346375-23c9450c58cd"), ("핫도그", "토스트", "스트리트")),
        FoodImage(_u("1585030013374-00a1dde83f9c"), ("순대", "국밥", "골목")),
    ),
    "cafe-dessert": (
        FoodImage(_u("1495474472287-4d71bcdd2085"), ("커피", "라떼", "핸드드립", "로스팅")),
        FoodImage(_u("1551024506-0bccd828d307"), ("케이크", "디저트", "티룸", "마카롱")),
        FoodImage(_u("1563805042-7684c019e1cb"), ("아이스크림", "젤라토", "시즌")),
        FoodImage(_u("1504754524776-8f4f37790ca0"), ("베이커리", "크루아상", "빵")),
        FoodImage(_u("1555507036-9741f9a178c1"), ("브런치", "팬케이크", "와플")),
        FoodImage(_u("1511381939413-8f2d043fb68a"), ("초콜릿", "핫초코", "디저트")),
        FoodImage(_u("1501339847302-ac426a4a7cbb"), ("한옥", "카페", "찻집", "말차")),
    ),
    "bar": (
        FoodImage(_u("1510812431401-41d2bd2722f3"), ("와인", "와인바", "치즈", "내추럴")),
        FoodImage(_u("1470337458703-46ad1756a187"), ("포차", "막걸리", "안주", "노가리")),
        FoodImage(_u("1514362546857-3bc165543547"), ("칵테일", "라운지", "바", "위스키")),
        FoodImage(_u("1572112862588-4c9d3f9f1f8d"), ("맥주", "치킨", "크래프트", "안주")),
        FoodImage(_u("1414235077428-338989a2e8c0"), ("루프탑", "야경", "칵테일")),
        FoodImage(_u("1608270586620-248524c67de9"), ("주점", "안주", "술")),
    ),
}

# 매장별 고정 이미지 (메뉴·대표 사진)
RESTAURANT_IMAGE_OVERRIDES: dict[str, str] = {
    "홍대 라멘야": _u("1569718212165-3a8278d5f624"),
    "스시 오마카세 이로": _u("1579584425555-c3ce17fd1871"),
    "이태원 돈카츠 하우스": _u("1623855248186-52f656884a59"),
    "대림 반점": _u("1525755662778-989d3524086e"),
    "왕십리 훠궈": _u("1585030013374-00a1dde83f9c"),
    "강남 딤섬": _u("1582878826629-29ae1f063f83"),
    "브런치 테이블": _u("1476124369491-e7addf5ef851"),
    "이탈리안 키친 로마": _u("1565299624946-b28f40a0ae38"),
    "스테이크 하우스 1875": _u("1546069901-ba9599a7e63c"),
    "타이 스트리트": _u("1559314809-0d155014e29e"),
    "쌀국수 하노이": _u("1582878826629-29ae1f063f83"),
    "인도 커리 하우스": _u("1585937421612-70a008296fbe"),
    "신촌 떡볶이 연구소": _u("1589314276789-4caa0cbc9c0b"),
    "성수 베이커리": _u("1504754524776-8f4f37790ca0"),
    "이태원 와인바 셀러": _u("1510812431401-41d2bd2722f3"),
    "홍대 포차거리": _u("1470337458703-46ad1756a187"),
    "노량진 회센터 프리미엄": _u("1600891964092-4316c288032e"),
    "강남 설렁탕 명가": _u("1604908177525-6831cbab1f1c"),
    "성수 솥뚜껑 삼겹": _u("1529042410759-befb1204b916"),
    "송파 텐동야": _u("1580822183893-049bb9a8e295"),
    "건대 마라탕 거리": _u("1563379091339-ee6e7e6c3e5a"),
    "연남 리조또 하우스": _u("1540189546936-380986bb09c8"),
}


def _seed_int(name: str) -> int:
    return int(hashlib.md5(name.encode("utf-8")).hexdigest()[:8], 16)


def _normalize_text(*parts: str) -> str:
    return re.sub(r"\s+", " ", " ".join(p for p in parts if p)).lower()


def _score_image(img: FoodImage, text: str) -> int:
    score = 0
    for tag in img.tags:
        if tag.lower() in text:
            score += 3
    return score


def image_url_for_restaurant(
    name: str,
    category_slug: str,
    description: str = "",
    *,
    menu_items: list[dict[str, Any]] | None = None,
) -> str:
    """매장명·설명·메뉴 키워드에 맞는 대표 이미지 URL."""
    if name in RESTAURANT_IMAGE_OVERRIDES:
        return RESTAURANT_IMAGE_OVERRIDES[name]

    menu_text = ""
    if menu_items:
        menu_text = " ".join(
            f"{m.get('name', '')} {m.get('note', '')}" for m in menu_items if isinstance(m, dict)
        )

    text = _normalize_text(name, description, menu_text)
    pool = CATEGORY_IMAGE_POOLS.get(category_slug) or CATEGORY_IMAGE_POOLS["hansik"]

    # 매장마다 고유·장르 맞춤: 이름 해시 윈도우 + 키워드 점수
    idx = _seed_int(name) % len(pool)
    window = min(8, len(pool))
    candidates = [pool[(idx + i) % len(pool)] for i in range(window)]
    best = max(candidates, key=lambda img: _score_image(img, text))
    # 동일 URL 중복 완화: 이름+카테고리 해시로 풀 내 오프셋 추가
    alt = pool[(_seed_int(f"{name}:{category_slug}") + _score_image(best, text)) % len(pool)]
    if _score_image(alt, text) >= _score_image(best, text):
        return alt.url
    return best.url


def apply_image_to_seed_row(row: dict[str, Any]) -> dict[str, Any]:
    """시드 행에 매칭 이미지 URL 설정."""
    row = {**row}
    row["image_url"] = image_url_for_restaurant(
        row["name"],
        row.get("category_slug", "hansik"),
        row.get("description", ""),
        menu_items=row.get("menu_items"),
    )
    return row
