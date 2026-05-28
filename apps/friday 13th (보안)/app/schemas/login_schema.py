from pydantic import BaseModel


class LoginSchema(BaseModel):
    username: str
    password: str

    def to_log_dict(self) -> dict:
        return {
            "username": self.username,
            "password": self.password,
        }
