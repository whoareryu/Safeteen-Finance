from __future__ import annotations

import pandas as pd

from titanic.adapter.outbound.strategies.passenger_survival_strategies import (
    RandomForestStrategy,
    SurvivalAlgorithmStrategy,
)
from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.passenger_rose_model_port import RoseModelPort


class RoseModelInteractor(RoseModelUseCase):

    def __init__(
        self,
        repository: RoseModelPort,
        strategy: SurvivalAlgorithmStrategy | None = None,
    ) -> None:
        self.repository = repository
        self._strategy: SurvivalAlgorithmStrategy = strategy or RandomForestStrategy()

    def set_strategy(self, strategy: SurvivalAlgorithmStrategy) -> None:
        self._strategy = strategy

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._strategy.fit(X_train, y_train)

    def predict_survival(self, X: pd.DataFrame) -> list[int]:
        return self._strategy.predict(X)

    async def introduce_myself(self, schema) -> RoseModelResponse:
        schema = RoseModelSchema(id=14, name="로즈 드윗 부카터 (Rose DeWitt Bukater)")
        return RoseModelResponse(id=schema.id, name=schema.name)
