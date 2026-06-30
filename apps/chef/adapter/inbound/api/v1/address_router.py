import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from chef.adapter.inbound.api.schemas.address_schema import (
    AddressCreateRequest,
    AddressDetailResponse,
    AddressSchema,
    AddressUploadResultSchema,
    ContactUploadSchema,
)
from chef.app.dtos.address_dto import AddressCreateCommand, AddressQuery
from chef.app.ports.input.address_use_case import AddressUseCase
from chef.dependencies.address_provider import get_address_use_case

"""
Chef Address Book
주소록 연락처 관리 라우터 (Google 연락처 CSV 업로드 지원)
"""

address_router = APIRouter(prefix="/address", tags=["chef-address"])


@address_router.get("/myself")
async def introduce_myself(
    use_case: AddressUseCase = Depends(get_address_use_case),
) -> dict:
    result = await use_case.introduce_myself(AddressQuery(id=3, name="Chef Address Book"))
    return {"id": result.id, "name": result.name}


@address_router.get("/contacts", response_model=list[AddressDetailResponse])
async def list_contacts(
    use_case: AddressUseCase = Depends(get_address_use_case),
) -> list[AddressDetailResponse]:
    results = await use_case.list_contacts()
    return [
        AddressDetailResponse(
            id=r.id, name=r.name, email=r.email,
            company=r.company, phone=r.phone,
        )
        for r in results
    ]


@address_router.post("/contacts", response_model=AddressDetailResponse)
async def add_contact(
    body: AddressCreateRequest,
    use_case: AddressUseCase = Depends(get_address_use_case),
) -> AddressDetailResponse:
    result = await use_case.add_contact(
        AddressCreateCommand(
            name=body.name,
            email=body.email,
            company=body.company,
            phone=body.phone,
        )
    )
    return AddressDetailResponse(
        id=result.id, name=result.name, email=result.email,
        company=result.company, phone=result.phone,
    )


@address_router.post(
    "/upload",
    response_model=AddressUploadResultSchema,
    summary="Google 연락처 CSV 파일 업로드",
)
async def upload_contacts(
    file: UploadFile = File(...),
    use_case: AddressUseCase = Depends(get_address_use_case),
) -> AddressUploadResultSchema:
    text = (await file.read()).decode("utf-8", errors="replace")
    rows = _parse_csv(text)
    return await use_case.upload_contacts(rows)


# ── CSV 파싱 헬퍼 ──────────────────────────────────────────────────────────

def _parse_csv(text: str) -> list[ContactUploadSchema]:
    if not text.strip():
        raise HTTPException(status_code=400, detail="빈 CSV 파일입니다.")
    reader = csv.DictReader(StringIO(text))
    if reader.fieldnames is None:
        raise HTTPException(status_code=400, detail="CSV 헤더를 읽을 수 없습니다.")
    rows = []
    for row in reader:
        normalized = _normalize_contact_row(row)
        if normalized:
            rows.append(ContactUploadSchema(**normalized))
    return rows


def _normalize_contact_row(row: dict) -> dict:
    """Google 연락처 CSV 컬럼명 → ContactUploadSchema 필드명으로 변환."""
    _COLUMN_MAP: dict[str, str] = {
        "first name":              "first_name",
        "middle name":             "middle_name",
        "last name":               "last_name",
        "phonetic first name":     "phonetic_first_name",
        "phonetic middle name":    "phonetic_middle_name",
        "phonetic last name":      "phonetic_last_name",
        "name prefix":             "name_prefix",
        "name suffix":             "name_suffix",
        "nickname":                "nickname",
        "file as":                 "file_as",
        "organization name":       "organization_name",
        "organization title":      "organization_title",
        "organization department": "organization_department",
        "birthday":                "birthday",
        "notes":                   "notes",
        "photo":                   "photo",
        "labels":                  "labels",
        "e-mail 1 - label":        "email_1_label",
        "e-mail 1 - value":        "email_1_value",
        "phone 1 - label":         "phone_1_label",
        "phone 1 - value":         "phone_1_value",
    }

    normalized: dict = {}
    for raw_key, value in row.items():
        if raw_key is None:
            continue
        key = raw_key.strip().lower()
        field = _COLUMN_MAP.get(key)
        if field:
            normalized[field] = value or None
    return normalized
