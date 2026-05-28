from typing import Any, Protocol


class WalterUseCasePort(Protocol):
    """Inbound에서 호출하는 입력 포트."""

    async def get_passenger_page(self, *, page: int, page_size: int) -> dict[str, Any]: ...
