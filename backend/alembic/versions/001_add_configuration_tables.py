"""Add ticker and API configuration tables

Revision ID: 001_add_configuration_tables
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_configuration_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ticker_configurations table
    op.create_table(
        'ticker_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('exchange', sa.String(length=50), nullable=False),
        sa.Column('tr_v4_id', sa.String(length=50), nullable=True),
        sa.Column('tr_v3_id', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ticker_configurations_id'), 'ticker_configurations', ['id'], unique=False)
    op.create_index(op.f('ix_ticker_configurations_ticker'), 'ticker_configurations', ['ticker'], unique=True)
    op.create_index('ix_ticker_configurations_ticker_active', 'ticker_configurations', ['ticker', 'is_active'], unique=False)

    # Create api_configurations table
    op.create_table(
        'api_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('api_key', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_configurations_id'), 'api_configurations', ['id'], unique=False)
    op.create_index(op.f('ix_api_configurations_service_name'), 'api_configurations', ['service_name'], unique=True)
    op.create_index('ix_api_configurations_service_active', 'api_configurations', ['service_name', 'is_active'], unique=False)


def downgrade() -> None:
    # Drop api_configurations table
    op.drop_index('ix_api_configurations_service_active', table_name='api_configurations')
    op.drop_index(op.f('ix_api_configurations_service_name'), table_name='api_configurations')
    op.drop_index(op.f('ix_api_configurations_id'), table_name='api_configurations')
    op.drop_table('api_configurations')

    # Drop ticker_configurations table
    op.drop_index('ix_ticker_configurations_ticker_active', table_name='ticker_configurations')
    op.drop_index(op.f('ix_ticker_configurations_ticker'), table_name='ticker_configurations')
    op.drop_index(op.f('ix_ticker_configurations_id'), table_name='ticker_configurations')
    op.drop_table('ticker_configurations')
