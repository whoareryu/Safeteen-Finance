from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.fare_vo import Fare
from titanic.domain.value_objects.pclass_vo import PClass


@dataclass(frozen=True)
class EconomicStatus:
    """객실 등급과 탑승 요금을 묶은 경제적 지위 임베디드 값 객체.

    survived 상관계수: pclass=-0.34 / fare=+0.26
    두 피처 간 상관계수: -0.55 (동일 개념 — "경제적 능력")
    """

    pclass: PClass
    fare: Fare

    @classmethod
    def from_raw(cls, pclass: str, fare: str) -> EconomicStatus:
        """원시 등급·요금 문자열로부터 EconomicStatus를 생성한다."""
        return cls(
            pclass=PClass.from_raw(pclass),
            fare=Fare.from_raw(fare),
        )

    @property
    def is_first_class(self) -> bool:
        return self.pclass.is_first_class

    @property
    def is_expensive(self) -> bool:
        return self.fare.is_expensive()

    @property
    def class_label(self) -> str:
        return self.pclass.label

    def __str__(self) -> str:
        return f"{self.pclass.label} / {self.fare}"
