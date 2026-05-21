import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# backend 루트를 path에 추가
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from apps.auth.user_model import User  # noqa: F401
from apps.gourmet.app.models.daily_recommendation import DailyRecommendation  # noqa: F401
from apps.gourmet.app.models.favorite import Favorite  # noqa: F401
from apps.gourmet.app.models.meal_plan import MealPlan  # noqa: F401
from apps.gourmet.app.models.restaurant import Restaurant  # noqa: F401
from apps.gourmet.app.models.search_query_log import SearchQueryLog  # noqa: F401
from apps.gourmet.app.models.sgma_restaurant import SgmaRestaurant  # noqa: F401
from apps.titanic.app.models.titanic_passenger import TitanicPassenger  # noqa: F401
from apps.database import Base, get_sync_database_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = get_sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_sync_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
