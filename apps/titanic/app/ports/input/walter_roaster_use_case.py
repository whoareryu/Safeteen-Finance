from abc import ABC, abstractmethod
from apps.titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterRoasterSchema

class WalterRoasterUseCase(ABC):
    
    @abstractmethod
    def introduce_myself(self, schema:WalterRoasterSchema):
        pass

