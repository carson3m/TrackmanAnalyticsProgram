"""add_team_metric_targets_table

Revision ID: 82e6062456c3
Revises: ed1ac9f89b49
Create Date: 2025-08-05 18:56:01.075804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82e6062456c3'
down_revision: Union[str, Sequence[str], None] = 'ed1ac9f89b49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('team_metric_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('metric_name', sa.String(), nullable=False),
        sa.Column('target_value', sa.Integer(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('lower_is_better', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('team_metric_targets')
