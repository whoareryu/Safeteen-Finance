from apps.friday_13th.app.ports.output.pamela_signup_repository import PamelaSignupRepository

class PamelaSignupPGRepository(PamelaSignupRepository):
    def __init__(self):
        pass

    async def signup(self, user: User) -> User:
        return await self.pamela_signup_repository.signup(user)

pamela_signup_pg_repository = PamelaSignupPGRepository()

