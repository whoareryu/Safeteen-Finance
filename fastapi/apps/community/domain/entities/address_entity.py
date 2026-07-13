from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AddressEntity:
    id: int
    name: str
    email: str
    company: str = ""
    phone: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AddressEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def introduce_myself(self) -> str:
        return f"AddressAgent(id={self.id}, name={self.name}, email={self.email})"

    def full_label(self) -> str:
        return f"{self.name} <{self.email}>"
