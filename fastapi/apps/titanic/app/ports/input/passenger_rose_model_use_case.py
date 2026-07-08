from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse


class SurvivalAlgorithmStrategy(ABC):
    """생존 예측 알고리즘 전략 인터페이스 (Strategy Pattern)."""

    @abstractmethod
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None: ...

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> list[int]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


class RoseModelUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/rose_model_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: RoseModelQuery) -> RoseModelResponse: ...
