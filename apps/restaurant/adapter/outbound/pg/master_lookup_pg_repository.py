"""3NF 마스터 조회·생성 (CSV·보강 적재용)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.biz_classification_orm import BizClassification
from restaurant.adapter.outbound.orm.sigungu_district_orm import SigunguDistrict
from restaurant.adapter.outbound.orm.tag_orm import Tag
from restaurant.utils.tag_slug import tag_slug_from_label


class SigunguDistrictRepository:
    def get_or_create_id(
        self, db: Session, *, sigungu_name: str, district_label: str
    ) -> int:
        sn = (sigungu_name or "").strip() or "미상"
        dl = (district_label or "").strip() or "미상"
        row = db.scalars(
            select(SigunguDistrict).where(
                SigunguDistrict.sigungu_name == sn,
                SigunguDistrict.district_label == dl,
            )
        ).first()
        if row is not None:
            return row.id
        row = SigunguDistrict(sigungu_name=sn, district_label=dl)
        db.add(row)
        db.flush()
        return row.id

    def ensure_default(self, db: Session) -> int:
        return self.get_or_create_id(db, sigungu_name="미상", district_label="미상")


class BizClassificationRepository:
    def get_or_create_id(
        self,
        db: Session,
        *,
        biz_mid_name: str,
        biz_minor_name: str,
        ksic_name: str,
    ) -> int:
        mid = (biz_mid_name or "").strip()
        minor = (biz_minor_name or "").strip()
        ksic = (ksic_name or "").strip()
        row = db.scalars(
            select(BizClassification).where(
                BizClassification.biz_mid_name == mid,
                BizClassification.biz_minor_name == minor,
                BizClassification.ksic_name == ksic,
            )
        ).first()
        if row is not None:
            return row.id
        row = BizClassification(
            biz_mid_name=mid,
            biz_minor_name=minor,
            ksic_name=ksic,
        )
        db.add(row)
        db.flush()
        return row.id

    def ensure_default(self, db: Session) -> int:
        return self.get_or_create_id(
            db, biz_mid_name="", biz_minor_name="", ksic_name=""
        )


class TagRepository:
    def get_or_create_id(self, db: Session, label: str) -> int:
        text = (label or "").strip()
        if not text:
            text = "tag"
        slug = tag_slug_from_label(text)
        row = db.scalars(select(Tag).where(Tag.slug == slug)).first()
        if row is not None:
            return row.id
        row = Tag(slug=slug, label=text[:128])
        db.add(row)
        db.flush()
        return row.id

