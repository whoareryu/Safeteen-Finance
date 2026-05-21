"""업로드 CSV → ``titanic_passengers`` (Neon) 적재."""

from __future__ import annotations

import io
import logging

import pandas as pd
from sqlalchemy import delete
from sqlalchemy.orm import Session

from apps.titanic.app.models.titanic_passenger import TitanicPassenger

logger = logging.getLogger(__name__)

_COLUMN_ALIASES: dict[str, str] = {
    "passengerid": "passenger_id",
    "survived": "survived",
    "pclass": "pclass",
    "name": "name",
    "sex": "sex",
    "age": "age",
    "sibsp": "sib_sp",
    "parch": "parch",
    "ticket": "ticket",
    "fare": "fare",
    "cabin": "cabin",
    "embarked": "embarked",
}

_REQUIRED = frozenset(_COLUMN_ALIASES.values())


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for col in df.columns:
        key = str(col).strip().lower().replace(" ", "_")
        if key in _COLUMN_ALIASES:
            rename[col] = _COLUMN_ALIASES[key]
    out = df.rename(columns=rename)
    missing = _REQUIRED - set(out.columns)
    if missing:
        raise ValueError(
            f"CSV에 필요한 컬럼이 없습니다: {', '.join(sorted(missing))}"
        )
    return out[list(_REQUIRED)]


def _cell_str(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()


def _cell_float(v) -> float | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _cell_int(v, default: int = 0) -> int:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return default
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def import_titanic_csv_to_db(db: Session, file_bytes: bytes) -> dict:
    """CSV 바이트를 파싱해 기존 행을 교체 적재."""
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"CSV를 읽을 수 없습니다: {e}") from e

    if df.empty:
        raise ValueError("CSV에 데이터 행이 없습니다.")

    df = _normalize_columns(df)
    deleted = db.execute(delete(TitanicPassenger)).rowcount or 0

    batch: list[TitanicPassenger] = []
    inserted = 0
    chunk = 500

    for row in df.itertuples(index=False):
        batch.append(
            TitanicPassenger(
                passenger_id=_cell_int(row.passenger_id),
                survived=_cell_int(row.survived),
                pclass=_cell_int(row.pclass),
                name=_cell_str(row.name) or "—",
                sex=_cell_str(row.sex) or "unknown",
                age=_cell_float(row.age),
                sib_sp=_cell_int(row.sib_sp),
                parch=_cell_int(row.parch),
                ticket=_cell_str(row.ticket),
                fare=_cell_float(row.fare),
                cabin=_cell_str(row.cabin),
                embarked=_cell_str(row.embarked),
            )
        )
        if len(batch) >= chunk:
            db.add_all(batch)
            db.commit()
            inserted += len(batch)
            batch.clear()

    if batch:
        db.add_all(batch)
        db.commit()
        inserted += len(batch)

    logger.info(
        "[titanic] CSV 적재 — 삭제(대략)=%s 삽입=%s",
        deleted,
        inserted,
    )
    return {
        "inserted": inserted,
        "deleted_previous": int(deleted),
        "table": TitanicPassenger.__tablename__,
    }
