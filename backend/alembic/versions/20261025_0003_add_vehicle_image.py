"""Add a local image filename to vehicles.

Revision ID: 20261025_0003
Revises: 20261025_0002
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa

revision = "20261025_0003"
down_revision = "20261025_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vehicles", sa.Column("image_filename", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("vehicles", "image_filename")
