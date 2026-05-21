"""타이타닉 Gemini 채팅 — CSV·(추후) DB ``titanic_passengers`` 컨텍스트 주입."""

from __future__ import annotations

import json
import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

# JamesController는 순환 참조 방지를 위해 함수 내에서 로컬 임포트합니다.

logger = logging.getLogger(__name__)

# CSV를 DB relation에 적재한 뒤 이 테이블명으로 조회 (없으면 CSV만 사용)
TITANIC_DB_TABLE = "titanic_passengers"
_CONTEXT_ROW_CAP = 8


def _context_from_db(db: Session) -> str | None:
    """``titanic_passengers`` 테이블이 있으면 DB 기반 요약."""
    try:
        total = db.execute(
            text(f"SELECT COUNT(*) FROM {TITANIC_DB_TABLE}")
        ).scalar_one()
        total = int(total or 0)
        if total <= 0:
            return None
        survived = db.execute(
            text(
                f"SELECT COUNT(*) FROM {TITANIC_DB_TABLE} WHERE survived = 1"
            )
        ).scalar_one()
        survived = int(survived or 0)
        sample = db.execute(
            text(
                f"SELECT * FROM {TITANIC_DB_TABLE} ORDER BY passenger_id LIMIT :lim"
            ),
            {"lim": _CONTEXT_ROW_CAP},
        ).mappings().all()
        rows = [dict(r) for r in sample]
        return (
            f"[데이터 출처: PostgreSQL 테이블 `{TITANIC_DB_TABLE}`]\n"
            f"- 전체 승객 수: {total}\n"
            f"- 생존(Survived=1): {survived}\n"
            f"- 사망: {total - survived}\n"
            f"- 샘플 {_CONTEXT_ROW_CAP}행:\n{json.dumps(rows, ensure_ascii=False, default=str)}"
        )
    except Exception:
        db.rollback()
        return None


def _context_from_csv() -> str:
    """로컬 ``Titanic-Dataset.csv`` 요약 (WalterReader / JamesController)."""
    from apps.titanic.app.controllers.james_controller import JamesController
    james = JamesController()
    df = james.service.walter.get_full_dataframe()
    total = int(len(df))
    survived = int(james.get_count_survived())
    dead = int(james.get_count_dead())
    model_name = james.get_training_model_name()
    accuracy = james.get_training_model_accuracy()
    has_tree = james.has_decision_tree_model()

    cols = ", ".join(str(c) for c in df.columns)
    desc = df.describe(include="all").astype(object).where(
        df.describe(include="all").notna(), None
    )
    desc_records = desc.to_dict()
    sample = (
        df.head(_CONTEXT_ROW_CAP)
        .astype(object)
        .where(df.head(_CONTEXT_ROW_CAP).notna(), None)
        .to_dict(orient="records")
    )

    by_sex = (
        df.groupby("Sex")["Survived"].agg(["count", "sum"])
        .reset_index()
        .to_dict(orient="records")
    )
    by_class = (
        df.groupby("Pclass")["Survived"].agg(["count", "sum"])
        .reset_index()
        .to_dict(orient="records")
    )

    return (
        "[데이터 출처: Titanic-Dataset.csv (파일)]\n"
        f"- 전체 승객 수: {total}\n"
        f"- 생존(Survived=1): {survived}\n"
        f"- 사망(Survived=0): {dead}\n"
        f"- 컬럼: {cols}\n"
        f"- 성별·생존 집계: {json.dumps(by_sex, ensure_ascii=False)}\n"
        f"- 객실등급·생존 집계: {json.dumps(by_class, ensure_ascii=False)}\n"
        f"- ML 모델: {model_name}, 결정트리 학습됨={has_tree}, 검증 정확도≈{accuracy:.3f}\n"
        f"- describe 요약: {json.dumps(desc_records, ensure_ascii=False, default=str)[:4000]}\n"
        f"- 샘플 {_CONTEXT_ROW_CAP}행:\n{json.dumps(sample, ensure_ascii=False, default=str)}"
    )


def build_titanic_chat_context(db: Session | None = None) -> str:
    """
    Gemini에 넣을 데이터 컨텍스트.
    DB ``titanic_passengers`` 가 있으면 우선, 없으면 CSV.
    """
    if db is not None:
        db_ctx = _context_from_db(db)
        if db_ctx:
            logger.info("[titanic chat] 컨텍스트 — DB `%s`", TITANIC_DB_TABLE)
            return db_ctx

    logger.info("[titanic chat] 컨텍스트 — CSV 파일")
    return _context_from_csv()


def augment_user_message_with_context(
    user_content: str,
    context: str,
) -> str:
    return (
        "당신은 타이타닉 승객 데이터 분석 도우미입니다. "
        "아래 [데이터 컨텍스트]에 있는 수치·표본만 근거로 답하고, "
        "컨텍스트에 없는 내용은 추측하지 말고 '데이터에 없습니다'라고 말하세요.\n\n"
        f"[데이터 컨텍스트]\n{context}\n\n"
        f"[사용자 질문]\n{user_content.strip()}"
    )
