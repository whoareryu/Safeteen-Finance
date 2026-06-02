from abc import ABC, abstractmethod



class LoginUseCase(ABC):
    @abstractmethod
    async def login(self, user: User) -> User:
        pass

