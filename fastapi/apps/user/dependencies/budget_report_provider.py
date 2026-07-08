from functools import lru_cache

from user.adapter.outbound.pg.budget_report_pg_repository import (
    BudgetReportPgRepository,
)
from user.app.ports.input.budget_report_use_case import BudgetReportUseCase
from user.app.use_cases.budget_report_interactor import BudgetReportInteractor


@lru_cache
def get_budget_report_use_case() -> BudgetReportUseCase:
    return BudgetReportInteractor(repository=BudgetReportPgRepository())
