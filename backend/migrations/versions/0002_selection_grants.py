"""Only explicitly selected snapshots have durable authorization."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0002_selection_grants"
down_revision = "0001_library"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "material_versions", sa.Column("extractor_metadata", JSONB(), nullable=True)
    )
    op.create_table(
        "selection_grants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "material_version_id",
            sa.Uuid(),
            sa.ForeignKey("material_versions.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("input_sha256", sa.String(64), nullable=False),
        sa.Column("source_origin_key", sa.Text(), nullable=False),
        sa.Column("raw_capture_sha256", sa.String(64), nullable=False),
        sa.Column("obtained_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("actor", sa.String(40), nullable=False),
        sa.Column("idempotency_hash", sa.String(64), nullable=True, unique=True),
        sa.CheckConstraint(
            "action = 'explicit_user_selection' AND actor = 'local_personal_user'"
        ),
    )


def downgrade():
    op.drop_table("selection_grants")
    op.drop_column("material_versions", "extractor_metadata")
