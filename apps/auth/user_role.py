from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    partner = "partner"
