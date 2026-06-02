from __future__ import annotations

from ..ports.input.andrews_blueprint_use_case import AndrewsBlueprintUseCase


class AndrewsBlueprintInteractor(AndrewsBlueprintUseCase):
    async def get_blueprint(self) -> dict[str, str]:
        return {"message": "Hello, World!"}
