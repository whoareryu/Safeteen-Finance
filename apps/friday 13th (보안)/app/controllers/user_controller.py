import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from sqlalchemy.orm import Session

from apps.database import DATABASE_INIT_ERROR, get_sync_db
from apps.auth.user_model import User
from apps.auth.user_role import UserRole
from apps.secom.app.schemas.login_schema import LoginSchema
from apps.secom.app.schemas.user_schema import UserSchema
from apps.secom.app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/secom", tags=["secom"])


class UserRegisterBody(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    nickname: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    password_confirm: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.USER

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return self


class UserPublicResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: str
    role: str
    role_label: str


def _db_unavailable() -> None:
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail=DATABASE_INIT_ERROR)


def _to_response(user: User) -> UserPublicResponse:
    labels = {
        UserRole.ADMIN: "사이트 관리자",
        UserRole.USER: "사이트사용유저",
        UserRole.PARTNER: "사이트등록유저",
    }
    return UserPublicResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        role=user.role.value,
        role_label=labels.get(user.role, user.role.value),
    )


class UserController:
    """main /signup 과 동일하게 service → repository 로 DB INSERT."""

    def save_user(self, user: UserSchema, db: Session) -> User:
        logger.info(
            "[UserController] save_user 진입 — payload=%s",
            user.to_log_dict(),
        )
        saved = UserService(db).save_user(user)
        logger.info(
            "[UserController] save_user 완료 — id=%s username=%s role=%s",
            saved.id,
            saved.username,
            saved.role.value,
        )
        return saved

    def login_user(self, credentials: LoginSchema, db: Session) -> User | None:
        logger.info(
            "[UserController] login_user 진입 — payload=%s",
            credentials.to_log_dict(),
        )
        found = UserService(db).login_user(credentials)
        if found:
            logger.info(
                "[UserController] login_user 완료 — id=%s username=%s",
                found.id,
                found.username,
            )
        else:
            logger.info("[UserController] login_user 완료 — 인증 실패")
        return found


@router.post("/users", response_model=UserPublicResponse, status_code=201)
def register_secom_user(
    body: UserRegisterBody, db: Session = Depends(get_sync_db)
):
    """users 테이블에 즉시 INSERT (secom 레이어)."""
    _db_unavailable()
    schema = UserSchema(
        username=body.username,
        email=str(body.email),
        nickname=body.nickname,
        password=body.password,
        role=body.role.value,
    )
    saved = UserController().save_user(schema, db)
    return _to_response(saved)
