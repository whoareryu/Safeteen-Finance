from __future__ import annotations

import numpy as np
import pandas as pd

from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.output.crew_lowe_boat_port import LoweBoatPort

_BINS = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
_AGE_LABELS = ["Unknown", "Baby", "Child", "Teenager", "Student", "Young Adult", "Adult", "Senior"]
_AGE_TITLE_MAP = {
    0: "Unknown", 1: "Baby", 2: "Child", 3: "Teenager",
    4: "Student", 5: "Young Adult", 6: "Adult", 7: "Senior",
}
_AGE_MAP = {v: k for k, v in _AGE_TITLE_MAP.items()}
_TITLE_MAP = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Royal": 5, "Rare": 6}
_DROP_COLS = ["Name", "Age", "Fare", "Ticket", "Cabin", "PassengerId"]


class LoweBoatInteractor(LoweBoatUseCase):

    def __init__(self, repository: LoweBoatPort):
        self.repository = repository

    def feature_engineering(self, train_set: pd.DataFrame) -> pd.DataFrame:
        train = train_set.copy()

        # 1. Label 분리
        y_label = train["Survived"].astype(int).tolist()  # noqa: F841 (caller may use)
        train = train.drop("Survived", axis=1)

        # 2. 호칭 추출 및 Nominal 변환
        train["Title"] = train["Name"].str.extract(r"([A-Za-z]+)\.", expand=False)
        train["Title"] = train["Title"].replace(
            ["Capt", "Col", "Don", "Dr", "Major", "Rev", "Jonkheer", "Dona", "Mme"], "Rare"
        )
        train["Title"] = train["Title"].replace(["Countess", "Lady", "Sir"], "Royal")
        train["Title"] = train["Title"].replace({"Mlle": "Mr", "Ms": "Miss"})
        train["Title"] = train["Title"].map(_TITLE_MAP).fillna(0).astype(int)

        # 3. 성별 Nominal 변환 (female=1, male=0)
        train["gender"] = train["gender"].map({"male": 0, "female": 1})

        # 4. 나이 구간 Ordinal 변환 및 결측치 처리
        train["Age"] = train["Age"].fillna(-0.5)
        train["AgeGroup"] = pd.cut(train["Age"], _BINS, labels=_AGE_LABELS).astype(str)
        mask = train["AgeGroup"] == "Unknown"
        train.loc[mask, "AgeGroup"] = train.loc[mask, "Title"].map(_AGE_TITLE_MAP)
        train["AgeGroup"] = train["AgeGroup"].map(_AGE_MAP).fillna(0).astype(int)

        # 5. 승선항 Nominal 변환
        train["Embarked"] = train["Embarked"].fillna("S").map({"S": 1, "C": 2, "Q": 3})

        # 6. 요금 Ordinal 변환 (4분위 구간)
        train["FareBand"] = (
            pd.qcut(train["Fare"], 4, labels=[1, 2, 3, 4], duplicates="drop")
            .fillna(1)
            .astype(int)
        )

        # 7. 불필요 컬럼 드롭
        train = train.drop(columns=[c for c in _DROP_COLS if c in train.columns])

        return train

    async def introduce_myself(self, schema) -> LoweBoatResponse:
        schema = LoweBoatSchema(id=5, name="해롤드 로우 (Harold Lowe)")
        return LoweBoatResponse(id=schema.id, name=schema.name)
