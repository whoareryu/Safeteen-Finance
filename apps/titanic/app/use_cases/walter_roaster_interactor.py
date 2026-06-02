from typing import Any

from titanic.app.ports.input.walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.output.walter_roaster_repository import WalterRoasterRepository


class WalterRoasterInteractor(WalterRoasterUseCase):
    def __init__(self, repository: WalterRoasterRepository) -> None:
        self._repository = repository

    async def list_paginated(self, page: int, page_size: int) -> dict[str, Any]:
        total, items = await self._repository.list_paginated(page, page_size)
        return {"total": total, "page": page, "page_size": page_size, "items": items}