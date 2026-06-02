"""타이타닉 조회·채팅 컨텍스트 유스케이스."""

from __future__ import annotations

import json
import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.titanic.app.use_cases.reader_use_case import ReaderUseCase
from apps.titanic.app.use_cases.rose_diamond_interactor import RoseModel

from ..ports.input.jack_sketch_use_case import JackSketchUseCase

logger = logging.getLogger(__name__)

TITANIC_DB_TABLE = "titanic_passengers"
_CONTEXT_ROW_CAP = 8


class JackSketchInteractor(JackSketchUseCase):
    async def get_sketch(self) -> dict[str, str]:
        return {"message": "Hello, World!"}


class JackService:
    """CSV·모델 조회 (TitanicReader 포트 구현)."""

    def __init__(self) -> None:
        self.walter = ReaderUseCase()
        self.rose = RoseModel()

    def get_data(self) -> dict:
        return self.walter.get_data()

    def get_count(self) -> int:
        return self.walter.get_count()

    def get_count_survived(self) -> int:
        return self.walter.get_count_survived()

    def get_count_dead(self) -> int:
        return self.walter.get_count_dead()

    def has_decision_tree_model(self) -> bool:
        return self.rose.has_decision_tree_model()

    def get_training_model_name(self) -> str:
        return self.rose.get_training_model_name()

    def get_training_model_accuracy(self) -> float:
        df = self.walter.get_full_dataframe()
        return self.rose.compute_training_accuracy(df)


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


def build_titanic_chat_context(db: Session | None = None) -> str:
    """Gemini에 넣을 데이터 컨텍스트."""
    if db is not None:
        db_ctx = _context_from_db(db)
        if db_ctx:
            logger.info("[titanic chat] 컨텍스트 — DB `%s`", TITANIC_DB_TABLE)
            return db_ctx

    logger.info("[titanic chat] 컨텍스트 — 없음")
    return (
        f"[데이터 출처: 없음]\n"
        f"- `{TITANIC_DB_TABLE}` 테이블이 없거나 비어 있습니다.\n"
        f"- 먼저 CSV를 업로드하거나(기능이 있다면) DB에 데이터를 적재한 뒤 다시 시도하세요."
    )


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
