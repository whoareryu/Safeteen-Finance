"""RBAC — 기존 apps/auth/user_role.py의 UserRole을 그대로 재사용한다.

문서(auth-gateway-harness.md 2.1)는 별도 Role/Permission 체계를 제안하지만,
지금 이 저장소 어디에도 role보다 세분화된 권한(Permission) 요구사항이 없어
새로 설계하지 않는다 — 실제 쓰이는 건 역할 기반 RoleChecker 하나뿐이다.
"""
from __future__ import annotations

from apps.auth.user_role import UserRole as Role
from core.dependencies import RoleChecker

__all__ = ["Role", "RoleChecker"]
