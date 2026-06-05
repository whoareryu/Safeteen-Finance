from __future__ import annotations

from gourmet.app.ports.output.daily_pick_repository import DailyPickRepository


class DailyPickPgRepository(DailyPickRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
