"""secom 레이어 — ORM 은 auth.User(`users` 테이블) 단일 사용."""

from apps.auth.user_model import User

# 기존 import 호환
SecUser = User

__all__ = ["SecUser", "User"]
