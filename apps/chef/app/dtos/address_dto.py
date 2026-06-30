from dataclasses import dataclass


@dataclass(frozen=True)
class AddressQuery:
    id: int
    name: str


@dataclass(frozen=True)
class AddressCreateCommand:
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
