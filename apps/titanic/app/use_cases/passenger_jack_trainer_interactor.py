from __future__ import annotations

from typing import Any

import pandas as pd
from kiwipiepy import Kiwi

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_jack_trainer_repository import JackTrainerRepository
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


class JackTrainerInteractor(JackTrainerUseCase):

    def __init__(self, repository: JackTrainerRepository):
        self.repository = repository
        self.kiwi = Kiwi()

    async def train_model(self, train_set) -> dict[str, Any]:
        records = await self.repository.get_training_data()
        if not records:
            return {"error": "훈련 데이터가 없습니다."}

        df = pd.DataFrame([
            {"survived": r.survived, "age": r.age, "sib_sp": r.sib_sp, "parch": r.parch, "gender": r.gender}
            for r in records
        ])
        X_train = df[_FEATURES]
        y_train = df["survived"]

        results: dict[str, Any] = {}
        for StrategyClass in _STRATEGIES:
            strategy = StrategyClass()
            try:
                strategy.fit(X_train, y_train)
                results[strategy.name] = {"status": "trained"}
            except Exception as exc:
                results[strategy.name] = {"status": "error", "message": str(exc)}

        return results

    async def analyze_message_intent(self, user_message: str) -> dict:
        tokens = self.kiwi.tokenize(user_message)

        keywords = [t.form for t in tokens if t.tag in ("NNG", "NNP", "SL", "SN")]

        forms = {t.form for t in tokens}
        if forms & {"몇", "수", "명수", "총", "얼마", "인원"}:
            intent = "count"
        elif forms & {"생존", "살아남", "살았", "구조"}:
            intent = "survival"
        elif forms & {"사망", "죽었", "죽다", "사망자"}:
            intent = "death"
        elif forms & {"평균", "나이", "연령"}:
            intent = "statistics"
        elif forms & {"성별", "여성", "남성", "여자", "남자"}:
            intent = "gender"
        elif forms & {"등석", "클래스", "pclass"}:
            intent = "class"
        else:
            intent = "unknown"

        return {"keywords": keywords, "intent": intent}

    async def introduce_myself(self, schema: JackTrainerSchema) -> JackTrainerResponse:
        return await self.repository.introduce_myself(JackTrainerQuery(
            id=schema.id,
            name=schema.name,
        ))
