from __future__ import annotations

from ..ports.input.hartley_violin_use_case import HartleyViolinUseCase


class HartleyViolinInteractor(HartleyViolinUseCase):
    async def get_violin(self) -> dict[str, str]:
        return {"message": "Hello, World!"}
