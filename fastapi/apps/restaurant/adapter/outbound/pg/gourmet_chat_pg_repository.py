from __future__ import annotations

from restaurant.app.ports.output.gourmet_chat_repository import GourmetChatRepository


class GourmetChatPgRepository(GourmetChatRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
