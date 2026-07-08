from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.embarked_vo import Embarked
from titanic.domain.value_objects.ticket_vo import TicketNumber


@dataclass(frozen=True)
class BoardingInfo:
    """티켓 번호와 탑승 항구를 묶은 탑승 정보 임베디드 값 객체.

    survived 상관계수: ticket=-0.20 / embarked=+0.11
    두 피처 모두 "어떻게 탑승했는가"를 나타냄.
    """

    ticket: TicketNumber
    embarked: Embarked

    @classmethod
    def from_raw(cls, ticket: str, embarked: str) -> BoardingInfo:
        """원시 티켓·항구 문자열로부터 BoardingInfo를 생성한다."""
        return cls(
            ticket=TicketNumber.from_raw(ticket),
            embarked=Embarked.from_raw(embarked),
        )

    @property
    def has_ticket_prefix(self) -> bool:
        """티켓 번호에 알파벳 접두어가 있으면 True (단체·특수 티켓)."""
        return self.ticket.prefix is not None

    @property
    def port_name(self) -> str:
        return self.embarked.label

    @property
    def is_boarded_at_cherbourg(self) -> bool:
        return self.embarked.raw == "C"

    def __str__(self) -> str:
        return f"{self.ticket} / {self.embarked.label}"
