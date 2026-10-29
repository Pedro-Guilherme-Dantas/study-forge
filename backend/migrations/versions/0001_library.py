"""Authorized library, source versions and atomic ingestion."""

from alembic import op
from pathlib import Path

revision = "0001_library"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    # Frozen DDL must not change when the application's ORM evolves.
    sql = Path(__file__).with_suffix(".sql").read_text()
    op.get_bind().exec_driver_sql(sql)


def downgrade():
    op.execute("ALTER TABLE materials DROP CONSTRAINT fk_material_active")
    for table in (
        "chunks",
        "ingestion_operations",
        "material_versions",
        "embedding_profiles",
        "materials",
    ):
        op.execute(f"DROP TABLE {table}")
