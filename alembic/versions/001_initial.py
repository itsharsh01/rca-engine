"""initial revision

Revision ID: 001
Revises: None
Create Date: 2026-07-11

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Upgrade database schema tables (Org, Project, App, Trace, Span)
    pass

def downgrade() -> None:
    pass
