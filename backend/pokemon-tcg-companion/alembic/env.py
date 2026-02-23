import asyncio
import importlib
import pkgutil

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from alembic import context
from core.db import _normalize_async_url
from core.settings import settings

config = context.config
config.set_main_option("sqlalchemy.url", _normalize_async_url(settings.database_url))


def load_models(package_names: list[str]) -> None:
    """
    Automatically discovers and imports all 'models' modules within the
    'package_names' list to ensure SQLModel knows about them.
    """

    for package_name in package_names:
        pkg = importlib.import_module(package_name)
        pkg_path = pkg.__path__

        for _finder, mod_name, _ispkg in pkgutil.walk_packages(
            pkg_path, prefix=package_name + "."
        ):
            # Import any direct "models" package or modules under a models package
            if mod_name.endswith(".models") or ".models." in mod_name:
                importlib.import_module(mod_name)


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    pkg_names_opt = config.get_main_option("package_names") or ""
    package_names = [p.strip() for p in pkg_names_opt.split(",") if p.strip()]

    load_models(package_names)

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=SQLModel.metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


run_migrations_online()
