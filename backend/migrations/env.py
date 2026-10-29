from alembic import context
from sqlalchemy import create_engine
from app.settings import get_settings

try:
    from app.db.models import Base

    target_metadata = Base.metadata
except ImportError:
    target_metadata = None

if context.is_offline_mode():
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(
        get_settings().database_url, echo=False, hide_parameters=True
    )
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
