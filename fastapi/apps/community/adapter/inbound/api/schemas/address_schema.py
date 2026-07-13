from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class AddressSchema(BaseModel):
    id: int = Field(3, description="Service ID")
    name: str = Field("Chef Address Book", description="Service name")

    model_config = {
        "json_schema_extra": {"example": {"id": 3, "name": "Chef Address Book"}}
    }


class AddressCreateRequest(BaseModel):
    name: str
    email: EmailStr
    company: str = ""
    phone: str = ""


class AddressDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    company: str
    phone: str


class ContactUploadSchema(BaseModel):
    """Google 연락처 내보내기 CSV 한 행."""
    first_name:              Optional[str] = Field(None, description="이름")
    middle_name:             Optional[str] = Field(None, description="중간 이름")
    last_name:               Optional[str] = Field(None, description="성")
    phonetic_first_name:     Optional[str] = None
    phonetic_middle_name:    Optional[str] = None
    phonetic_last_name:      Optional[str] = None
    name_prefix:             Optional[str] = None
    name_suffix:             Optional[str] = None
    nickname:                Optional[str] = None
    file_as:                 Optional[str] = None
    organization_name:       Optional[str] = Field(None, description="회사")
    organization_title:      Optional[str] = None
    organization_department: Optional[str] = None
    birthday:                Optional[str] = None
    notes:                   Optional[str] = None
    photo:                   Optional[str] = None
    labels:                  Optional[str] = None
    email_1_label:           Optional[str] = None
    email_1_value:           Optional[str] = Field(None, description="이메일 주소")
    phone_1_label:           Optional[str] = None
    phone_1_value:           Optional[str] = Field(None, description="전화번호")

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Jun",
                "last_name": "Ryu",
                "organization_name": "Anthropic",
                "email_1_value": "fbwns1234@gmail.com",
                "phone_1_value": "010-1234-5678",
            }
        }
    }


class AddressUploadResultSchema(BaseModel):
    saved: int = Field(..., description="저장된 연락처 수")
