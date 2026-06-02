import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from apps.friday_13th.adapter.inbound.api.schemas.friday_wiring import build_login_use_case
from apps.friday_13th.app.ports.input.login_use_case import LoginCredentials, LoginUseCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

login_use_case: LoginUseCase = build_login_use_case()


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=1, max_length=128)


class UserPublicResponse(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    role: str


@router.post("/login", response_model=UserPublicResponse)
async def login_user(body: LoginRequest) -> UserPublicResponse:
    """inbound → ports/input → use_cases → ports/output → outbound/pg → DB"""
    logger.info("[Login] inbound → ports/input | username=%s", body.username)
    try:
        result = await login_use_case.login(
            LoginCredentials(username=body.username, password=body.password)
        )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        ) from None
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return UserPublicResponse(
        id=result.id,
        username=result.username,
        nickname=result.nickname,
        email=result.email,
        role=result.role,
    )
