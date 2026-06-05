import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, UploadFile

from titanic.adapter.inbound.api.schemas.james_director_schema import (
    TitanicRecordSchema,
    UploadResultSchema,
)
from titanic.app.dtos.james_director_dto import JamesDirectorResponse
from titanic.app.ports.input.james_director_use_case import JamesDirectorUseCase
from titanic.dependencies.james_director import get_james_director_use_case

'''
 james_director_router.py
 전설적인 흥행작 <타이타닉>을 연출하여
 "내가 세상의 왕이다!"를 외친 제임스 카메론 감독의 라우터
 완벽주의 성향으로 타이타닉의 모든 세트와 디테일을
 고증한 아키텍처의 총괄 디렉터 역할 수행
'''

james_director_router = APIRouter(prefix="/james", tags=["james"])


@james_director_router.post("/upload", response_model=JamesDirectorResponse)
async def upload_titanic_file(
    file: UploadFile = File(...),
    james: JamesDirectorUseCase = Depends(get_james_director_use_case),
):
    return await james.upload_titanic_file(
        _parse_csv((await file.read()).decode("utf-8", errors="replace"))
    )


def _parse_csv(text: str) -> list[TitanicRecordSchema]:
    reader = csv.DictReader(StringIO(text))
    return [TitanicRecordSchema(**_normalize_titanic_row(row)) for row in reader]


def _normalize_titanic_row(row: dict) -> dict:
    normalized: dict = {}
    for raw_key, value in row.items():
        if raw_key is None:
            continue
        key = raw_key.strip()
        lower_key = key.lower()
        if lower_key == "sex":
            normalized["gender"] = value
        elif lower_key == "passengerid":
            normalized["passenger_id"] = value
        elif lower_key == "sibsp":
            normalized["sib_sp"] = value
        elif lower_key in {
            "survived",
            "pclass",
            "name",
            "age",
            "parch",
            "ticket",
            "fare",
            "cabin",
            "embarked",
            "gender",
        }:
            normalized[lower_key] = value
        else:
            normalized[key] = value
    return normalized
