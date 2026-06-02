from pydantic import BaseModel, Field


class LoginSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=1, max_length=128)

    def to_log_dict(self) -> dict:
        return {"username": self.username, "password": "***"}
