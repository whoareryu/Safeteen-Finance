from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.walter_roaster_schema import WalterRoasterSchema

class WalterRoasterUseCase(ABC):
    
    @abstractmethod
    def introduce_myself(self, schema:WalterRoasterSchema):
        pass

