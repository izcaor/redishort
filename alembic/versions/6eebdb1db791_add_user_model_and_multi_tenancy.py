"""Add User model and multi-tenancy

Revision ID: 6eebdb1db791
Revises:
Create Date: 2026-04-22 13:00:10.871958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6eebdb1db791'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if we need to create the initial tables or just add the columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'users' not in tables:
        op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
            batch_op.create_index(batch_op.f('ix_users_id'), ['id'], unique=False)

    if 'video_projects' not in tables:
        # creating all since it wasn't there
        op.create_table('video_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('NEW', 'DRAFTING', 'PENDING_APPROVAL', 'PROCESSING', 'COMPLETED', 'FAILED', name='workflowstate'), nullable=False),
        sa.Column('script', sa.Text(), nullable=True),
        sa.Column('youtube_title', sa.String(), nullable=True),
        sa.Column('youtube_desc', sa.Text(), nullable=True),
        sa.Column('narrator_gender', sa.String(), nullable=True),
        sa.Column('video_path', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('video_projects', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_video_projects_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_video_projects_source_id'), ['source_id'], unique=False)
    else:
        # the table exists, add the user_id column
        with op.batch_alter_table('video_projects', schema=None) as batch_op:
            batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_video_projects_user_id', 'users', ['user_id'], ['id'])

    if 'content_sources' not in tables:
        op.create_table('content_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('source_url', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('last_fetched_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('content_sources', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_content_sources_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_content_sources_source_type'), ['source_type'], unique=False)
            batch_op.create_index(batch_op.f('ix_content_sources_source_url'), ['source_url'], unique=True)
    else:
        # the table exists, add the user_id column
        with op.batch_alter_table('content_sources', schema=None) as batch_op:
            batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_content_sources_user_id', 'users', ['user_id'], ['id'])

def downgrade() -> None:
    pass
