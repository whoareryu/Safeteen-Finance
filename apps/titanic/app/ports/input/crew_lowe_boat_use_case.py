from __future__ import annotations
from abc import ABC, abstractmethod

import pandas as pd

from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse


class LoweBoatUseCase(ABC):
    """Inbound input port."""
    @abstractmethod
    async def introduce_myself(self, schema: LoweBoatQuery) -> LoweBoatResponse:
        pass


    @abstractmethod
    def feature_engineering(self, train_set) -> pd.DataFrame:
        ''''''
        
        pass