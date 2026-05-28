from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    nickname: str
    role: str = Field(description="admin | user | partner")

    def to_log_dict(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "password": self.password,
            "role": self.role,
        }
