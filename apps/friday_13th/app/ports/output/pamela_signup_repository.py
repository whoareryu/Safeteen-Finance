from abc import ABC, abstractmethod

class PamelaSignupRepository(ABC):
    @abstractmethod
    async def signup(self, user: User) -> User:
        pass

