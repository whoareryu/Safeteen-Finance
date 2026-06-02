from abc import ABC, abstractmethod

class PamelaSignupUseCase(ABC):
    @abstractmethod
    async def signup(self, user: User) -> User:
        pass
