"""add qr image, make target_url nullable

Revision ID: c1f4a7d2e8b3
Revises: 9bd438a8d5c8
Create Date: 2026-09-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1f4a7d2e8b3'
down_revision: Union[str, None] = '9bd438a8d5c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'dynamic_payment_urls',
        sa.Column('qr_image', sa.LargeBinary(), nullable=True),
    )
    op.add_column(
        'dynamic_payment_urls',
        sa.Column('qr_image_type', sa.String(length=50), nullable=True),
    )
    op.alter_column(
        'dynamic_payment_urls',
        'target_url',
        existing_type=sa.String(length=500),
        nullable=True,
    )


def downgrade() -> None:
    op.execute(
        "UPDATE dynamic_payment_urls SET target_url = '' WHERE target_url IS NULL"
    )
    op.alter_column(
        'dynamic_payment_urls',
        'target_url',
        existing_type=sa.String(length=500),
        nullable=False,
    )
    op.drop_column('dynamic_payment_urls', 'qr_image_type')
    op.drop_column('dynamic_payment_urls', 'qr_image')
