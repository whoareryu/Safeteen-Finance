from abc import ABC, abstractmethod




class UserRepositoryPort(ABC):
    @abstractmethod
    async def login(self, user: User) -> User:
        pass

