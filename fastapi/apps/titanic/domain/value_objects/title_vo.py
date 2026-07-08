from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


_RARE_TITLES = frozenset({"Capt", "Col", "Don", "Dr", "Major", "Rev", "Jonkheer", "Dona", "Mme"})
_ROYAL_TITLES = frozenset({"Countess", "Lady", "Sir"})
_ALIAS: dict[str, str] = {"Mlle": "Mr", "Ms": "Miss"}
_LABEL_TO_CODE: dict[str, int] = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Royal": 5, "Rare": 6}


@dataclass(frozen=True)
class TitleVO:
    """호칭(Title) 피처를 표현하는 값 객체."""

    label: str  # 정규화된 호칭 ("Mr", "Miss", "Mrs", "Master", "Royal", "Rare")
    code: int   # 인코딩 정수 (1-6, 미지 0)

    @property
    def is_rare(self) -> bool:
        return self.label == "Rare"

    @property
    def is_royal(self) -> bool:
        return self.label == "Royal"

    @property
    def is_unknown(self) -> bool:
        return self.code == 0

    @classmethod
    def from_raw(cls, raw: str) -> TitleVO:
        """원시 호칭 문자열로부터 TitleVO를 생성한다."""
        if raw in _RARE_TITLES:
            label = "Rare"
        elif raw in _ROYAL_TITLES:
            label = "Royal"
        else:
            label = _ALIAS.get(raw, raw)
        return cls(label=label, code=_LABEL_TO_CODE.get(label, 0))

    @staticmethod
    def encode_series(name_series: pd.Series) -> pd.Series:
        """Name Series에서 Title을 추출하여 인코딩된 정수 Series를 반환한다."""
        titles = name_series.str.extract(r"([A-Za-z]+)\.", expand=False)
        titles = titles.replace(list(_RARE_TITLES), "Rare")
        titles = titles.replace(list(_ROYAL_TITLES), "Royal")
        titles = titles.replace(_ALIAS)
        return titles.map(_LABEL_TO_CODE).fillna(0).astype(int)
