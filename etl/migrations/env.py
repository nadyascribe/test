import logging
from alembic import context, op
from alembic_utils.replaceable_entity import register_entities
from sqlalchemy import engine_from_config, pool

from dags.storage.models.asbom import MAT_VIEWS
from dags.storage.models.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

register_entities(MAT_VIEWS)


def _do_not_include_alembic_version(name, type_, schema):
    # don't include the alembic_version table
    if type_ == "table" and name in ("alembic_version",):
        return False
    if type_ == "schema" and (name in ("public", "app") or name is None):
        return False

    return True


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in ("alembic_version",):
        return False
    if type_ == "schema" and (name in ("public", "app") or name is None):
        return False

    skip = not getattr(object, "info", {}).get("skip_autogenerate")
    return skip


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    args = context.get_x_argument(as_dictionary=True)
    if args.get("sqlc-migrations", False):
        logging.getLogger("airflow").setLevel(logging.ERROR)
        logging.getLogger("alembic").setLevel(logging.ERROR)
    _set_connection()
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema="osint",
        include_name=_do_not_include_alembic_version,
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    _set_connection()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="osint",
            include_name=_do_not_include_alembic_version,
            include_object=include_object,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


def _set_connection():
    # import locally to prevent extra airflow logging
    from dags.storage import get_hook

    # use the same database as specified within airflow connections
    config.set_section_option("alembic", "sqlalchemy.url", get_hook().get_uri())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
