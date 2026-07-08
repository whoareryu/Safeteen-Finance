"""CSV 한 행 → 정제된 도메인 행 (결측·중복 키 처리)."""

from __future__ import annotations

from dataclasses import dataclass

from restaurant.data.ingestion.category_normalizer import CategoryNormalizer
from restaurant.data.restaurant_images import image_url_for_restaurant


@dataclass(frozen=True, slots=True)
class CleanedRestaurantRow:
    """``Restaurant`` ORM 적재 직전 불변 행."""

    biz_number: str
    name: str
    store_name: str
    branch_name: str
    category_slug: str
    category_label: str
    district: str
    sigungu_name: str
    road_address: str
    parcel_address: str
    latitude: float | None
    longitude: float | None
    avg_price: int | None
    signature_menu: str
    ai_tags: list[str]
    description: str
    image_url: str
    biz_mid_name: str
    biz_minor_name: str
    ksic_name: str


class RestaurantCsvRowCleaner:
    """결측치·카테고리 표준화·1인 추정 식대·AI 태그 초안."""

    _DEFAULT_AVG_PRICE_BY_SLUG: dict[str, int] = {
        "hansik": 15_000,
        "ilsik": 18_000,
        "jungsik": 14_000,
        "yangsik": 22_000,
        "asian": 16_000,
        "bunsik": 9_000,
        "cafe-dessert": 8_500,
        "bar": 25_000,
    }

    def __init__(self, normalizer: CategoryNormalizer | None = None) -> None:
        self._normalizer = normalizer or CategoryNormalizer()

    @staticmethod
    def _display_name(store_name: str, branch_name: str) -> str:
        s, b = (store_name or "").strip(), (branch_name or "").strip()
        if s and b:
            return f"{s} ({b})"
        return s or b or "상호 미상"

    @staticmethod
    def _district(sigungu: str, admin_dong: str, legal_dong: str) -> str:
        gu = (sigungu or "").strip()
        dong = (admin_dong or "").strip() or (legal_dong or "").strip()
        parts = [p for p in (gu, dong) if p]
        return " ".join(parts) if parts else ""

    @staticmethod
    def _safe_float(cell: str) -> float | None:
        t = (cell or "").strip()
        if not t:
            return None
        try:
            return float(t)
        except ValueError:
            return None

    def _infer_ai_tags(self, slug: str, biz_minor: str, ksic: str) -> list[str]:
        text = f"{biz_minor} {ksic}"
        tags: list[str] = []
        if slug in ("cafe-dessert", "bar"):
            tags.append("분위기")
        if "치킨" in text or "분식" in slug:
            tags.append("가성비")
        if "구이" in text or "고기" in text:
            tags.append("든든한")
        if not tags:
            tags.append("로컬")
        return tags[:5]

    def clean(self, raw: dict[str, str]) -> CleanedRestaurantRow | None:
        biz = (raw.get("상가업소번호") or "").strip()
        if not biz:
            return None

        store = (raw.get("상호명") or "").strip() or "미상"
        branch = (raw.get("지점명") or "").strip()
        mid_n = (raw.get("상권업종중분류명") or "").strip()
        min_n = (raw.get("상권업종소분류명") or "").strip()
        ksic_n = (raw.get("표준산업분류명") or "").strip()

        slug, label = self._normalizer.from_biz_fields(mid_n, min_n, ksic_n)
        name = self._display_name(store, branch)
        district = self._district(
            raw.get("시군구명") or "",
            raw.get("행정동명") or "",
            raw.get("법정동명") or "",
        )
        sigungu = (raw.get("시군구명") or "").strip()
        road = (raw.get("도로명주소") or "").strip()
        parcel = (raw.get("지번주소") or "").strip()
        lat = self._safe_float(raw.get("위도") or "")
        lng = self._safe_float(raw.get("경도") or "")

        signature = min_n or ksic_n or label
        avg_price = self._DEFAULT_AVG_PRICE_BY_SLUG.get(slug)
        ai_tags = self._infer_ai_tags(slug, min_n, ksic_n)
        desc_parts = [p for p in (min_n, ksic_n) if p]
        description = " · ".join(desc_parts) if desc_parts else label
        image_url = image_url_for_restaurant(name, slug, description)

        return CleanedRestaurantRow(
            biz_number=biz,
            name=name,
            store_name=store,
            branch_name=branch,
            category_slug=slug,
            category_label=label,
            district=district,
            sigungu_name=sigungu,
            road_address=road,
            parcel_address=parcel,
            latitude=lat,
            longitude=lng,
            avg_price=avg_price,
            signature_menu=signature[:256],
            ai_tags=ai_tags,
            description=description,
            image_url=image_url,
            biz_mid_name=mid_n,
            biz_minor_name=min_n,
            ksic_name=ksic_n,
        )
