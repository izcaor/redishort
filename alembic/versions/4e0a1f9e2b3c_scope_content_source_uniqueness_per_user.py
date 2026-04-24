"""Scope content source uniqueness per user

Revision ID: 4e0a1f9e2b3c
Revises: 6eebdb1db791
Create Date: 2026-04-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e0a1f9e2b3c'
down_revision: Union[str, Sequence[str], None] = '6eebdb1db791'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    index_names = {index['name'] for index in inspector.get_indexes('content_sources')}
    unique_constraint_names = {
        constraint['name']
        for constraint in inspector.get_unique_constraints('content_sources')
        if constraint.get('name')
    }

    with op.batch_alter_table('content_sources', schema=None) as batch_op:
        if 'ix_content_sources_source_url' in index_names:
            batch_op.drop_index('ix_content_sources_source_url')

        # Defensive cleanup for environments that created a unique constraint name.
        if 'uq_content_sources_source_url' in unique_constraint_names:
            batch_op.drop_constraint('uq_content_sources_source_url', type_='unique')

        if 'uq_content_sources_user_id_source_url' not in unique_constraint_names:
            batch_op.create_unique_constraint(
                'uq_content_sources_user_id_source_url',
                ['user_id', 'source_url'],
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    unique_constraint_names = {
        constraint['name']
        for constraint in inspector.get_unique_constraints('content_sources')
        if constraint.get('name')
    }

    with op.batch_alter_table('content_sources', schema=None) as batch_op:
        if 'uq_content_sources_user_id_source_url' in unique_constraint_names:
            batch_op.drop_constraint('uq_content_sources_user_id_source_url', type_='unique')

        batch_op.create_index('ix_content_sources_source_url', ['source_url'], unique=True)
