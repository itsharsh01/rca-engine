"""diagnosis revision

Revision ID: 002
Revises: 001
Create Date: 2026-07-11

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Adds Diagnosis table + indexes
    pass

def downgrade() -> None:
    pass
