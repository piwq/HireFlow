"""add_tz_compliance_tables

Revision ID: tz_compliance_001
Revises:
Create Date: 2026-04-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'tz_compliance_001'
down_revision: Union[str, None] = '0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_blocked to users
    op.add_column('users', sa.Column('is_blocked', sa.Boolean(), server_default='false', nullable=False))

    # Add photo_url to candidate_profiles
    op.add_column('candidate_profiles', sa.Column('photo_url', sa.String(500), nullable=True))

    # Add invitation_status to interviews
    op.add_column('interviews', sa.Column('invitation_status', sa.String(20), nullable=True))

    # Create work_experiences table
    op.create_table(
        'work_experiences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidate_profiles.id'), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('position', sa.String(255), nullable=False),
        sa.Column('start_date', sa.String(20), nullable=True),
        sa.Column('end_date', sa.String(20), nullable=True),
        sa.Column('is_current', sa.Boolean(), default=False),
        sa.Column('responsibilities', sa.Text(), nullable=True),
        sa.Column('achievements', sa.Text(), nullable=True),
        sa.Column('stack', sa.Text(), nullable=True),
    )

    # Create educations table
    op.create_table(
        'educations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidate_profiles.id'), nullable=False),
        sa.Column('institution', sa.String(255), nullable=False),
        sa.Column('faculty', sa.String(255), nullable=True),
        sa.Column('start_date', sa.String(20), nullable=True),
        sa.Column('end_date', sa.String(20), nullable=True),
        sa.Column('degree', sa.String(100), nullable=True),
    )

    # Create languages table
    op.create_table(
        'languages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidate_profiles.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('level', sa.String(50), nullable=True),
    )

    # Create project_certificates table
    op.create_table(
        'project_certificates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidate_profiles.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('date', sa.String(20), nullable=True),
        sa.Column('url', sa.String(500), nullable=True),
    )

    # Create notes table
    op.create_table(
        'notes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidate_profiles.id'), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('notes')
    op.drop_table('project_certificates')
    op.drop_table('languages')
    op.drop_table('educations')
    op.drop_table('work_experiences')
    op.drop_column('interviews', 'invitation_status')
    op.drop_column('candidate_profiles', 'photo_url')
    op.drop_column('users', 'is_blocked')
