import enum


class UserRole(str, enum.Enum):
    """사이트 보안 역할 — admin: 사이트 관리자, user: 사이트사용유저, partner: 사이트등록유저"""

    ADMIN = "admin"
    USER = "user"
    PARTNER = "partner"
