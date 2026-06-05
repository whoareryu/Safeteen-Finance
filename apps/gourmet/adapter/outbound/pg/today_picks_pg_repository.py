from __future__ import annotations

from gourmet.app.ports.output.today_picks_repository import TodayPicksRepository


class TodayPicksPgRepository(TodayPicksRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
