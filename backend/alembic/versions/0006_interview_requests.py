"""Add interview_requests table

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("manager_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidate_profiles.id"), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("preferred_format", sa.String(20), nullable=True),
        sa.Column("preferred_time", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("interview_requests")
