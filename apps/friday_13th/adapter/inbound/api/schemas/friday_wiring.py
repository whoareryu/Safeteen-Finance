"""Composition root — UseCase·Outbound 구현체 조립 (DB 연결은 outbound/pg 에만 둠)."""

from __future__ import annotations

from apps.friday_13th.adapter.outbound.pg.user_pg_repository import UserPGRepositoryAdapter
from apps.friday_13th.app.ports.input.login_use_case import LoginUseCase
from apps.friday_13th.app.use_cases.login_interactor import LoginInteractor


def build_login_use_case() -> LoginUseCase:
    return LoginInteractor(repository=UserPGRepositoryAdapter())
