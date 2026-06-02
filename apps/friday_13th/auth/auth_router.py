import logging
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.friday_13th.auth.dependencies import get_current_user
from apps.friday_13th.auth.password import hash_password, verify_password
from apps.friday_13th.auth.user_model import User
from apps.friday_13th.auth.user_role import UserRole
from apps.database import DATABASE_INIT_ERROR, get_sync_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


class UsernameCheckResponse(BaseModel):
    username: str
    available: bool
    message: str


class NicknameCheckResponse(BaseModel):
    nickname: str
    available: bool
    message: str


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=6, max_length=128)
    password_confirm: str = Field(..., min_length=6, max_length=128)
    email: EmailStr
    nickname: str = Field(..., min_length=1, max_length=64)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not _USERNAME_RE.match(v):
            raise ValueError(
                "아이디는 영문, 숫자, 밑줄(_)만 사용 가능하며 3~32자여야 합니다."
            )
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return self


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=1, max_length=128)


class UserPublic(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    role: str = Field(..., description="admin | user | partner")


def _user_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        role=user.role.value,
    )


def _db_unavailable() -> None:
    if DATABASE_INIT_ERROR:
        raise HTTPException(
            status_code=503,
            detail="데이터베이스에 연결할 수 없습니다. DATABASE_URL을 확인해 주세요.",
        )


def _username_taken(db: Session, username: str) -> bool:
    normalized = username.strip().lower()
    return (
        db.execute(
            select(User.id).where(func.lower(User.username) == normalized).limit(1)
        ).scalar_one_or_none()
        is not None
    )


def _nickname_taken(db: Session, nickname: str) -> bool:
    normalized = nickname.strip().lower()
    return (
        db.execute(
            select(User.id).where(func.lower(User.nickname) == normalized).limit(1)
        ).scalar_one_or_none()
        is not None
    )


@router.get("/check-username", response_model=UsernameCheckResponse)
def check_username(
    username: str = Query(..., min_length=3, max_length=32),
    db: Session = Depends(get_sync_db),
):
    _db_unavailable()
    name = username.strip()
    if not _USERNAME_RE.match(name):
        raise HTTPException(
            status_code=400,
            detail="아이디는 영문, 숫자, 밑줄(_)만 사용 가능하며 3~32자여야 합니다.",
        )
    try:
        taken = _username_taken(db, name)
    except Exception:
        logger.exception("아이디 중복 확인 실패")
        raise HTTPException(
            status_code=503, detail="아이디 중복 확인 중 오류가 발생했습니다."
        ) from None

    if taken:
        return UsernameCheckResponse(
            username=name,
            available=False,
            message="이미 사용 중인 아이디입니다. 다른 아이디를 사용해 주세요.",
        )
    return UsernameCheckResponse(
        username=name,
        available=True,
        message="사용 가능한 아이디입니다.",
    )


@router.get("/check-nickname", response_model=NicknameCheckResponse)
def check_nickname(
    nickname: str = Query(..., min_length=1, max_length=64),
    db: Session = Depends(get_sync_db),
):
    _db_unavailable()
    nick = nickname.strip()
    if not nick:
        raise HTTPException(status_code=400, detail="닉네임을 입력해 주세요.")

    try:
        taken = _nickname_taken(db, nick)
    except Exception:
        logger.exception("닉네임 중복 확인 실패")
        raise HTTPException(
            status_code=503, detail="닉네임 중복 확인 중 오류가 발생했습니다."
        ) from None

    if taken:
        return NicknameCheckResponse(
            nickname=nick,
            available=False,
            message="사용중인 닉네임입니다.",
        )
    return NicknameCheckResponse(
        nickname=nick,
        available=True,
        message="사용 가능한 닉네임입니다.",
    )


@router.post("/signup", response_model=UserPublic, status_code=201)
def signup(body: SignupRequest, db: Session = Depends(get_sync_db)):
    _db_unavailable()
    if body.password != body.password_confirm:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    if _username_taken(db, body.username):
        raise HTTPException(
            status_code=409,
            detail="이미 사용 중인 아이디입니다. 다른 아이디를 사용해 주세요.",
        )

    if _nickname_taken(db, body.nickname):
        raise HTTPException(status_code=409, detail="사용중인 닉네임입니다.")

    if (
        db.execute(select(User).where(User.email == body.email.lower()).limit(1))
        .scalar_one_or_none()
    ):
        raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")

    user = User(
        username=body.username.strip(),
        email=body.email.lower(),
        nickname=body.nickname.strip(),
        password_hash=hash_password(body.password),
        role=UserRole.USER,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        logger.exception("회원가입 DB 저장 실패")
        raise HTTPException(status_code=500, detail="회원가입 처리 중 오류가 발생했습니다.") from None

    logger.info(
        "[auth] users 테이블 INSERT 완료 — id=%s username=%s email=%s nickname=%s role=%s",
        user.id,
        user.username,
        user.email,
        user.nickname,
        user.role.value,
    )
    return _user_public(user)


# 로그인은 adapter/inbound/api/v1/login_router.py (클린 헥사고날) 로 처리합니다.


@router.get("/me", response_model=UserPublic)
def read_current_user(user: User = Depends(get_current_user)):
    """localStorage에 저장된 ``user.id`` → ``X-User-Id`` 헤더로 검증·갱신."""
    _db_unavailable()
    return _user_public(user)


class AdminUserRow(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    role: str
    created_at: str | None


def _require_admin(db: Session, username: str) -> User:
    actor = db.execute(
        select(User).where(func.lower(User.username) == username.strip().lower()).limit(1)
    ).scalar_one_or_none()
    if actor is None or actor.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return actor


@router.get("/admin/users", response_model=list[AdminUserRow])
def list_users_for_admin(
    as_username: str = Query(..., description="요청자 로그인 아이디"),
    db: Session = Depends(get_sync_db),
):
    """고객관리 — admin 전용 회원 목록."""
    _db_unavailable()
    _require_admin(db, as_username)
    rows = db.execute(select(User).order_by(User.id)).scalars().all()
    return [
        AdminUserRow(
            id=u.id,
            username=u.username,
            nickname=u.nickname,
            email=u.email,
            role=u.role.value,
            created_at=u.created_at.isoformat() if u.created_at else None,
        )
        for u in rows
    ]
