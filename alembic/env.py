from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from sqlalchemy import MetaData

from alembic import context

config = context.config
fileConfig(config.config_file_name)

def get_fake_meta(engine, exclude_table):
    meta = MetaData(bind=engine, reflect=True)
    for t in meta.sorted_tables:
        if t.name == exclude_table:
            meta.remove(t)
    return meta

sqllite_engine = create_engine('sqlite:///data/bandit.db')
# TODO: гипотеза - нужно, чтобы этот объект не включал в обновленные данные в БД. Дропнем таблицу df
target_metadata = get_fake_meta(sqllite_engine, 'df')



def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
