from __future__ import annotations

import re
from dataclasses import dataclass

from titanic.domain.value_objects.gender_vo import Gender
from titanic.domain.value_objects.title_vo import TitleVO


@dataclass(frozen=True)
class PassengerIdentity:
    """성별과 호칭을 묶은 승객 정체성 임베디드 값 객체.

    survived 상관계수: gender=+0.54 / title=+0.47
    두 피처 간 상관계수: 0.72 (동일 개념 — "누구인가")
    """

    gender: Gender
    title: TitleVO

    @classmethod
    def from_raw(cls, sex: str, name: str) -> PassengerIdentity:
        """원시 성별 문자열과 이름 문자열로부터 PassengerIdentity를 생성한다."""
        match = re.search(r"([A-Za-z]+)\.", name)
        raw_title = match.group(1) if match else ""
        return cls(
            gender=Gender.from_raw(sex),
            title=TitleVO.from_raw(raw_title),
        )

    @property
    def is_female(self) -> bool:
        return self.gender.is_female

    @property
    def is_privileged(self) -> bool:
        return self.title.is_royal

    @property
    def is_rare_title(self) -> bool:
        return self.title.is_rare

    @property
    def title_code(self) -> int:
        return self.title.code

    def __str__(self) -> str:
        return f"{self.gender} / {self.title.label}"
