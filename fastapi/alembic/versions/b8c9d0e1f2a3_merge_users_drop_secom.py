"""merge secom_users into users, drop secom_users

Revision ID: b8c9d0e1f2a3
Revises: a1b2c3d4e5f6
Create Date: 2026-05-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())

    if "users" in tables:
        cols = {c["name"] for c in insp.get_columns("users")}
        if "role" not in cols:
            op.add_column(
                "users",
                sa.Column(
                    "role",
                    sa.Enum(
                        "admin",
                        "user",
                        "partner",
                        name="user_role",
                        native_enum=False,
                    ),
                    nullable=False,
                    server_default="user",
                ),
            )
            op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
        if "last_login_at" not in cols:
            op.add_column(
                "users",
                sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
            )

    if "secom_users" in tables:
        if "users" in tables:
            op.execute(sa.text(
                "INSERT INTO users (username, email, nickname, password_hash, role, created_at) "
                "SELECT s.username, s.email, s.nickname, s.password_hash, s.role::text, s.created_at "
                "FROM secom_users s "
                "WHERE NOT EXISTS (SELECT 1 FROM users u WHERE lower(u.username) = lower(s.username))"
            ))
        op.drop_index(op.f("ix_secom_users_username"), table_name="secom_users")
        op.drop_index(op.f("ix_secom_users_role"), table_name="secom_users")
        op.drop_index(op.f("ix_secom_users_nickname"), table_name="secom_users")
        op.drop_index(op.f("ix_secom_users_email"), table_name="secom_users")
        op.drop_table("secom_users")
        op.execute(sa.text("DROP TYPE IF EXISTS secom_user_role"))


def downgrade() -> None:
    op.create_table(
        "secom_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("nickname", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "admin", "user", "partner", name="secom_user_role", native_enum=False
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_secom_users_username"), "secom_users", ["username"], unique=True
    )
