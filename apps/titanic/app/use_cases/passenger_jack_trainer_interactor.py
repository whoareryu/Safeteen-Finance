from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from titanic.adapter.outbound.strategies.passenger_survival_strategies import ALL_STRATEGIES
from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_jack_trainer_port import JackTrainerPort

logger = logging.getLogger(__name__)


class JackTrainerInteractor(JackTrainerUseCase):

    def __init__(self, repository: JackTrainerPort):
        self.repository = repository
        self._trained_strategies: dict = {}

    async def train_model(self, train_set: pd.DataFrame) -> dict[str, Any]:
        '''로즈가 제안한 모델들을 훈련시키는 메소드'''
        logger.info("[JackTrainerInteractor] 학습 파이프라인 시작")

        _FEATURES = ["age", "sib_sp", "parch", "gender"]

        if train_set.empty:
            return {"train_samples": 0, "trained_models": [], "trained_strategies": {}}

        train = train_set.dropna(subset=["survived"]).copy()
        train["gender"] = train["gender"].map({"male": 0, "female": 1}).fillna(0).astype(int)
        y_label: list[int] = train["survived"].astype(int).tolist()
        X_train: list[list[float]] = train[_FEATURES].fillna(0).values.tolist()

        self._trained_strategies = {}
        trained_names = []
        for StrategyClass in ALL_STRATEGIES:
            strategy = StrategyClass()
            try:
                strategy.fit(X_train, y_label)
                self._trained_strategies[strategy.name] = strategy
                trained_names.append(strategy.name)
                logger.info(f"[JackTrainerInteractor] {strategy.name} 학습 완료")
            except Exception as e:
                logger.warning(f"[JackTrainerInteractor] {strategy.name} 학습 실패 | error={e}")

        return {
            "train_samples": len(X_train),
            "trained_models": trained_names,
            "trained_strategies": self._trained_strategies,
        }

    

    async def introduce_myself(self, schema) -> JackTrainerResponse:
        schema = JackTrainerSchema(id=13, name="잭 도슨 (Jack Dawson)")
        return JackTrainerResponse(id=schema.id, name=schema.name)