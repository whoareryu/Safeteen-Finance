from __future__ import annotations

from ..ports.input.ruth_corset_use_case import RuthCorsetUseCase


class RuthCorsetInteractor(RuthCorsetUseCase):
    async def get_corset(self) -> dict[str, str]:
        return {"message": "Hello, World!"}
