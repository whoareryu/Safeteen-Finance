from __future__ import annotations

from ..ports.input.cal_pistol_use_case import CalPistolUseCase


class ValidationUseCase:
    """Validation Use Case."""

    pass


class CalPistolInteractor(CalPistolUseCase):
    async def get_cal_pistol(self) -> dict[str, str]:
        return {"message": "Hello, World!"}
