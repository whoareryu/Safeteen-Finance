"""사용자 role 변경.

사용:
  cd backend
  python scripts/set_user_role.py Whoareryu admin
"""

from __future__ import annotations

import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from dotenv import load_dotenv

load_dotenv(_backend_root / ".env")

from sqlalchemy import func, select

from apps.auth.user_model import User
from apps.auth.user_role import UserRole
from apps.database import SyncSessionLocal


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python scripts/set_user_role.py <username> <admin|user|partner>")
        sys.exit(1)

    username = sys.argv[1].strip()
    role_name = sys.argv[2].strip().lower()
    try:
        role = UserRole(role_name)
    except ValueError:
        print(f"Invalid role: {role_name}")
        sys.exit(1)

    if SyncSessionLocal is None:
        print("DB not initialized")
        sys.exit(1)

    db = SyncSessionLocal()
    try:
        user = db.execute(
            select(User).where(func.lower(User.username) == username.lower()).limit(1)
        ).scalar_one_or_none()
        if user is None:
            print(f"User not found: {username}")
            sys.exit(1)
        user.role = role
        db.commit()
        print(f"OK: {user.username} -> {user.role.value}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
