"""폐업 식당 정리 스크립트 (기획서 6-1 데이터 구축).

서울 식당 인허가 CSV(LOCALDATA형)에서 **영업상태가 폐업**인 행을 찾아:
  1. 영업중 행만 남긴 정제 CSV 생성  (import 용)
  2. 폐업 사업장번호 목록(txt) 생성
  3. restaurants 테이블 DELETE SQL(.sql) 생성

기본은 **dry-run** — DB를 건드리지 않고 위 산출물만 만든다.
실제 Neon DB에서 삭제하려면 사용자가 직접 ``--execute`` 로 실행한다.

CSV 컬럼명은 데이터셋마다 다르므로 아래 상수로 분리했다.
서울시 일반음식점 인허가(LOCALDATA) 기준 기본값이며, 받은 파일의 헤더와
다르면 상수만 수정한다.

사용:
    python scripts/clean_closed_restaurants.py --csv /path/seoul.csv
    python scripts/clean_closed_restaurants.py            # RESTAURANTS_CSV 사용
    python scripts/clean_closed_restaurants.py --execute   # DB DELETE까지 실행
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("clean_closed")

# ── CSV 컬럼 매핑 (받은 파일 헤더에 맞게 조정) ──────────────────
COL_BIZ_NUMBER = "관리번호"  # restaurants.biz_number 와 매칭되는 고유키
COL_STATUS = "영업상태명"  # "영업/정상" vs "폐업"
COL_STATUS_DETAIL = "상세영업상태명"  # 보조 판별 (폐업/말소/취소)
CLOSED_TOKENS = ("폐업", "말소", "취소", "직권말소")

# CSV 인코딩 후보 (공공데이터는 CP949가 많음)
ENCODINGS = ("utf-8-sig", "cp949", "euc-kr", "utf-8")


def _open_csv(path: Path):
    last_err: Exception | None = None
    for enc in ENCODINGS:
        try:
            f = path.open("r", encoding=enc, newline="")
            f.readline()
            f.seek(0)
            logger.info("[csv] 인코딩 감지: %s", enc)
            return f
        except (UnicodeDecodeError, LookupError) as e:  # noqa: PERF203
            last_err = e
    raise UnicodeError(f"인코딩 판별 실패: {path} ({last_err})")


def _is_closed(row: dict[str, str]) -> bool:
    status = (row.get(COL_STATUS) or "").strip()
    detail = (row.get(COL_STATUS_DETAIL) or "").strip()
    blob = f"{status} {detail}"
    return any(tok in blob for tok in CLOSED_TOKENS)


def split_rows(csv_path: Path) -> tuple[list[dict], list[str], list[str]]:
    """(영업중 행, 폐업 biz_number, 헤더) 반환."""
    with _open_csv(csv_path) as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV 헤더를 읽지 못했습니다.")
        header = list(reader.fieldnames)
        for required in (COL_BIZ_NUMBER, COL_STATUS):
            if required not in header:
                raise KeyError(
                    f"컬럼 '{required}' 없음. 스크립트 상단 상수를 헤더에 맞게 수정하세요.\n"
                    f"발견된 헤더: {header}"
                )
        active: list[dict] = []
        closed_ids: list[str] = []
        for row in reader:
            if _is_closed(row):
                biz = (row.get(COL_BIZ_NUMBER) or "").strip()
                if biz:
                    closed_ids.append(biz)
            else:
                active.append(row)
    return active, closed_ids, header


def write_outputs(
    csv_path: Path, active: list[dict], closed_ids: list[str], header: list[str]
) -> tuple[Path, Path, Path]:
    stem = csv_path.with_suffix("")
    active_csv = Path(f"{stem}.active.csv")
    closed_txt = Path(f"{stem}.closed_biz_numbers.txt")
    delete_sql = Path(f"{stem}.delete_closed.sql")

    with active_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(active)

    closed_txt.write_text("\n".join(closed_ids), encoding="utf-8")

    if closed_ids:
        values = ",".join("'" + b.replace("'", "''") + "'" for b in closed_ids)
        sql = (
            "-- GourmetMate 폐업 식당 삭제 (검토 후 수동 실행)\n"
            "BEGIN;\n"
            f"DELETE FROM restaurants WHERE biz_number IN ({values});\n"
            "COMMIT;\n"
        )
    else:
        sql = "-- 폐업 식당 없음\n"
    delete_sql.write_text(sql, encoding="utf-8")
    return active_csv, closed_txt, delete_sql


def execute_delete(closed_ids: list[str]) -> int:
    """--execute 전용. restaurants 에서 폐업 행 삭제."""
    if not closed_ids:
        logger.info("[db] 삭제 대상 없음")
        return 0
    # 지연 import — dry-run 경로는 DB 의존성 불필요
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from sqlalchemy import create_engine, text  # noqa: PLC0415

    from apps.database import get_sync_database_url  # noqa: PLC0415

    engine = create_engine(get_sync_database_url())
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM restaurants WHERE biz_number = ANY(:ids)"),
            {"ids": closed_ids},
        )
    deleted = result.rowcount or 0
    logger.info("[db] %s개 삭제 완료", deleted)
    return deleted


def main() -> None:
    parser = argparse.ArgumentParser(description="폐업 식당 정리")
    parser.add_argument(
        "--csv",
        default=os.getenv("RESTAURANTS_CSV"),
        help="식당 CSV 경로 (미지정 시 RESTAURANTS_CSV 환경변수)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="설정 시 Neon DB에서 실제 DELETE 실행 (기본: 산출물만 생성)",
    )
    args = parser.parse_args()

    if not args.csv:
        parser.error("--csv 또는 RESTAURANTS_CSV 가 필요합니다.")
    csv_path = Path(args.csv).expanduser()
    if not csv_path.is_file():
        parser.error(f"파일 없음: {csv_path}")

    active, closed_ids, header = split_rows(csv_path)
    logger.info(
        "[scan] 영업중 %s · 폐업 %s (총 %s)",
        len(active),
        len(closed_ids),
        len(active) + len(closed_ids),
    )
    active_csv, closed_txt, delete_sql = write_outputs(
        csv_path, active, closed_ids, header
    )
    logger.info("[out] 정제 CSV : %s", active_csv)
    logger.info("[out] 폐업 목록 : %s", closed_txt)
    logger.info("[out] DELETE SQL: %s", delete_sql)

    if args.execute:
        execute_delete(closed_ids)
    else:
        logger.info("[dry-run] DB 미변경. 삭제하려면 --execute 또는 위 .sql 실행.")


if __name__ == "__main__":
    main()
