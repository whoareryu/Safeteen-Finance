from __future__ import annotations

from ..ports.input.isidor_bed_use_case import IsidorBedUseCase


class IsidorBedInteractor(IsidorBedUseCase):
    async def get_bed(self) -> dict[str, str]:
        return {"message": "Hello, World!"}
