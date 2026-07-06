from abc import ABC, abstractmethod


class OwnerGatePort(ABC):
    @abstractmethod
    def is_owner(self, owner_session: str | None) -> bool: ...
