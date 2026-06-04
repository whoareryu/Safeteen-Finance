from titanic.app.ports.input.walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.dtos.walter_roaster_dto import WalterRoasterQuery
from titanic.app.repositories.walter_roaster_repository import WalterRoasterRepository

class WalterRoasterInteractor(WalterRoasterUseCase):
    
    def __init__(self):
        pass

    def introduce_myself(self):
        query = WalterRoasterQuery()
        pass

