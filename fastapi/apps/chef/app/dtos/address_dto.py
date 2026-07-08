from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AddressQuery:
    id: int
    name: str


@dataclass(frozen=True)
class AddressCreateCommand:
    user_id: int
    name: str
    email: str
    company: str = ""
    phone: str = ""


@dataclass(frozen=True)
class AddressResponse:
    id: int
    name: str


@dataclass(frozen=True)
class AddressDetailResult:
    id: int
    name: str
    email: str
    company: str
    phone: str


@dataclass(frozen=True)
class ContactUploadDto:
    """Google 연락처 CSV 한 행의 도메인 표현."""
    email_1_value: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    nickname: str | None = None
    organization_name: str | None = None
    organization_title: str | None = None
    phone_1_value: str | None = None
    birthday: str | None = None
    notes: str | None = None
    labels: str | None = None


@dataclass(frozen=True)
class AddressUploadResult:
    saved: int
