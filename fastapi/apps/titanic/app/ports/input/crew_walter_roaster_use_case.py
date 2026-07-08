from abc import ABC, abstractmethod

import pandas as pd

from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery, WalterRoasterResponse


class WalterRoasterUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: WalterRoasterQuery) -> WalterRoasterResponse:
        pass

    @abstractmethod
    async def get_train_set(self) -> pd.DataFrame:
        '''월터가 DB에서 train set 만 가져오는 메소드'''
        pass

    @abstractmethod
    async def get_test_set(self) -> pd.DataFrame:
        '''월터가 DB에서 test set 만 가져오는 메소드'''
        pass