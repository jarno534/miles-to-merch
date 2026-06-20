"""Add phase3 columns: print_areas on variant, sponsored_settings on product

Revision ID: phase3_001
Revises: 
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


# revision identifiers
revision = 'phase3_001'
down_revision = None
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column already exists in the table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # Add print_areas JSON column to variant table (if not exists)
    if not column_exists('variant', 'print_areas'):
        with op.batch_alter_table('variant', schema=None) as batch_op:
            batch_op.add_column(sa.Column('print_areas', sa.JSON(), nullable=True))

    # Add sponsored_settings JSON column to product table (if not exists)
    if not column_exists('product', 'sponsored_settings'):
        with op.batch_alter_table('product', schema=None) as batch_op:
            batch_op.add_column(sa.Column('sponsored_settings', sa.JSON(), nullable=True))


def downgrade():
    if column_exists('product', 'sponsored_settings'):
        with op.batch_alter_table('product', schema=None) as batch_op:
            batch_op.drop_column('sponsored_settings')

    if column_exists('variant', 'print_areas'):
        with op.batch_alter_table('variant', schema=None) as batch_op:
            batch_op.drop_column('print_areas')
