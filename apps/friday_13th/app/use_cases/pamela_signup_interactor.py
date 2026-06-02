from apps.friday_13th.app.ports.input.pamela_signup_use_case import PamelaSignupUseCase
from apps.friday_13th.app.ports.output.pamela_signup_repository import PamelaSignupRepository

class PamelaSignupInteractor(PamelaSignupUseCase):
    def __init__(self, pamela_signup_repository: PamelaSignupRepository):
        self.pamela_signup_repository = pamela_signup_repository

    async def signup(self, user: User) -> User:
        return await self.pamela_signup_repository.signup(user)

pamela_signup_interactor = PamelaSignupInteractor(PamelaSignupRepository())

