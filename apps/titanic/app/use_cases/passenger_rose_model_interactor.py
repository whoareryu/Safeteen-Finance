from __future__ import annotations

import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.passenger_rose_model_repository import RoseModelRepository


class RoseModel:
    def __init__(self) -> None:
        self.model = DecisionTreeClassifier(random_state=42)

    def get_model(self) -> str:
        return type(self.model).__name__

    def has_decision_tree_model(self) -> bool:
        return isinstance(self.model, DecisionTreeClassifier)

    def get_training_model_name(self) -> str:
        return type(self.model).__name__

    def compute_training_accuracy(self, df: pd.DataFrame) -> float:
        work = df.copy()
        drop_cols = [c for c in ("PassengerId", "Name", "Ticket", "Cabin") if c in work.columns]
        work = work.drop(columns=drop_cols)
        work["Sex"] = (work["Sex"] == "female").astype(int)
        if "Embarked" in work.columns:
            mode = work["Embarked"].mode()
            work["Embarked"] = work["Embarked"].fillna(mode.iloc[0] if len(mode) else "S")
            work = pd.get_dummies(work, columns=["Embarked"], dtype=int)
        work["Age"] = work["Age"].fillna(work["Age"].median())
        work["Fare"] = work["Fare"].fillna(work["Fare"].median())

        y = work["Survived"]
        X = work.drop(columns=["Survived"])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.model = DecisionTreeClassifier(random_state=42)
        self.model.fit(X_train, y_train)
        pred = self.model.predict(X_test)
        return float(accuracy_score(y_test, pred))


class RoseModelInteractor(RoseModelUseCase):
    
    def __init__(self, repository: RoseModelRepository):
        self.repository = repository

    async def introduce_myself(self, schema: RoseModelSchema) -> RoseModelResponse:
        '''로즈 모델의 자기소개 인터렉트'''
        query = RoseModelQuery(
            id = schema.id,
            name = schema.name
        )
        return await self.repository.introduce_myself(RoseModelQuery(
            id = schema.id,
            name = schema.name
        ))
        