import csv
import io

from fastapi import APIRouter, File, HTTPException, UploadFile

from apps.titanic.adapter.inbound.api.schemas.titanic_request import (
    TitanicPassengerRequest,
)
from apps.titanic.app.ports.input.james_use_case import JamesUseCase

james_router = APIRouter(prefix="/titanic/james", tags=["james"])
james_use_case = JamesUseCase()

_REQUIRED_COLUMNS = (
    "PassengerId",
    "Survived",
    "Pclass",
    "Name",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Ticket",
    "Fare",
    "Cabin",
    "Embarked",
)

# /titanic/james/upload 엔드포인트: CSV 파일 업로드
@james_router.post("/upload")
async def upload_titanic_csv(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드할 수 있습니다.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="빈 파일은 업로드할 수 없습니다.")

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="UTF-8 CSV만 지원합니다.",
        ) from exc

    reader = csv.DictReader(io.StringIO(text))
    headers = tuple(reader.fieldnames or [])
    missing = [col for col in _REQUIRED_COLUMNS if col not in headers]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"필수 컬럼이 없습니다: {', '.join(missing)}",
        )

    rows: list[dict] = []
    errors: list[str] = []
    for idx, row in enumerate(reader, start=2):
        if not row or not any((v or "").strip() for v in row.values()):
            continue
        try:
            payload = TitanicPassengerRequest.model_validate(row)
            # 요청대로 Sex 컬럼을 gender 키로 변환한 결과를 반환
            rows.append(payload.model_dump())
        except Exception as exc:
            errors.append(f"{idx}행: {exc}")
            if len(errors) >= 10:
                break

    if errors:
        raise HTTPException(
            status_code=422,
            detail={"message": "CSV 검증 실패", "errors": errors},
        )

    result = await james_use_case.handle_uploaded_rows(columns=[*headers], rows=rows)
    return {
        "ok": result.ok,
        "message": result.message,
        "count": result.count,
        "columns": result.columns,
        "rows": result.rows,
    }
