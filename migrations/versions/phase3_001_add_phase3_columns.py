"""Add phase3 columns: print_areas on variant, sponsored_settings on product

Revision ID: phase3_001
Revises: 
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'phase3_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add print_areas JSON column to variant table
    with op.batch_alter_table('variant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('print_areas', sa.JSON(), nullable=True))

    # Add sponsored_settings JSON column to product table
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sponsored_settings', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('sponsored_settings')

    with op.batch_alter_table('variant', schema=None) as batch_op:
        batch_op.drop_column('print_areas')
