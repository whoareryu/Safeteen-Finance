from __future__ import annotations

from ..ports.input.smith_captain_use_case import SmithCaptainUseCase


class SmithCaptainInteractor(SmithCaptainUseCase):
    async def get_captain(self) -> dict[str, str]:
        return {"message": "Hello, World!"}
