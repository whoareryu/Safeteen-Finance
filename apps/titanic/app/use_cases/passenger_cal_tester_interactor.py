from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.output.passenger_cal_tester_repository import CalTesterRepository
from titanic.app.use_cases.passenger_rose_model_interactor import (
    CatBoostStrategy,
    DecisionTreeStrategy,
    EnsemblePCAStrategy,
    KNNStrategy,
    LightGBMStrategy,
    LogisticRegressionStrategy,
    NaiveBayesStrategy,
    RandomForestStrategy,
    SVMStrategy,
    XGBoostStrategy,
)

_STRATEGIES = [
    XGBoostStrategy,
    RandomForestStrategy,
    LightGBMStrategy,
    CatBoostStrategy,
    LogisticRegressionStrategy,
    DecisionTreeStrategy,
    SVMStrategy,
    KNNStrategy,
    NaiveBayesStrategy,
    EnsemblePCAStrategy,
]

_FEATURES = ["age", "sib_sp", "parch", "gender"]


class CalTesterInteractor(CalTesterUseCase):

    def __init__(self, repository: CalTesterRepository):
        self.repository = repository

    async def test_model(self, test_set) -> dict[str, Any]:
        records = await self.repository.get_testing_data()
        if not records:
            return {"error": "테스트 데이터가 없습니다."}

        df = pd.DataFrame([
            {"survived": r.survived, "age": r.age, "sib_sp": r.sib_sp, "parch": r.parch, "gender": r.gender}
            for r in records
        ])
        X = df[_FEATURES]
        y = df["survived"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scores: dict[str, float] = {}
        for StrategyClass in _STRATEGIES:
            strategy = StrategyClass()
            try:
                strategy.fit(X_train, y_train)
                preds = strategy.predict(X_test)
                scores[strategy.name] = round(accuracy_score(y_test, preds), 4)
            except Exception as exc:
                scores[strategy.name] = -1.0

        valid_scores = {name: score for name, score in scores.items() if score >= 0}
        if not valid_scores:
            return {"error": "모든 모델 평가에 실패했습니다."}

        rankings = sorted(valid_scores.items(), key=lambda x: x[1], reverse=True)
        best_name, best_score = rankings[0]

        return {
            "winner": best_name,
            "winner_accuracy": best_score,
            "rankings": [
                {"rank": i + 1, "model": name, "accuracy": score}
                for i, (name, score) in enumerate(rankings)
            ],
        }

    async def introduce_myself(self, schema: CalTesterSchema) -> CalTesterResponse:
        return await self.repository.introduce_myself(CalTesterQuery(
            id=schema.id,
            name=schema.name,
        ))
