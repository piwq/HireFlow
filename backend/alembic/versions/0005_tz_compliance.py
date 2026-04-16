"""TZ compliance: new statuses, candidate fields, interview fields, feedback structure, status history, documents

Revision ID: 0005
Revises: e31b4e148ea6
Create Date: 2026-04-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, None] = "e31b4e148ea6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add admin role to userrole enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin'")

    # Add new application statuses
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'manager_interview'")
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'interview_done'")
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'awaiting_decision'")
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'reserve'")
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'offer'")
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'accepted'")

    # Add extended candidate profile fields
    op.add_column("candidate_profiles", sa.Column("phone", sa.String(50), nullable=True))
    op.add_column("candidate_profiles", sa.Column("city", sa.String(100), nullable=True))
    op.add_column("candidate_profiles", sa.Column("citizenship", sa.String(100), nullable=True))
    op.add_column("candidate_profiles", sa.Column("birth_date", sa.String(20), nullable=True))
    op.add_column("candidate_profiles", sa.Column("linkedin", sa.String(255), nullable=True))
    op.add_column("candidate_profiles", sa.Column("github", sa.String(255), nullable=True))
    op.add_column("candidate_profiles", sa.Column("portfolio", sa.String(255), nullable=True))
    op.add_column("candidate_profiles", sa.Column("desired_position", sa.String(255), nullable=True))
    op.add_column("candidate_profiles", sa.Column("specialization", sa.String(255), nullable=True))
    op.add_column("candidate_profiles", sa.Column("level", sa.String(50), nullable=True))
    op.add_column("candidate_profiles", sa.Column("salary_from", sa.Integer(), nullable=True))
    op.add_column("candidate_profiles", sa.Column("salary_to", sa.Integer(), nullable=True))
    op.add_column("candidate_profiles", sa.Column("employment_type", sa.String(100), nullable=True))
    op.add_column("candidate_profiles", sa.Column("work_format", sa.String(100), nullable=True))
    op.add_column("candidate_profiles", sa.Column("relocation_ready", sa.Boolean(), nullable=True))

    # Add interview fields
    op.add_column("interviews", sa.Column("format", sa.String(20), nullable=True))
    op.add_column("interviews", sa.Column("location", sa.String(500), nullable=True))
    op.add_column("interviews", sa.Column("comment", sa.Text(), nullable=True))
    op.add_column("interviews", sa.Column("manager_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))

    # Add structured feedback fields
    op.add_column("feedbacks", sa.Column("score_overall", sa.Integer(), nullable=True))
    op.add_column("feedbacks", sa.Column("score_technical", sa.Integer(), nullable=True))
    op.add_column("feedbacks", sa.Column("score_communication", sa.Integer(), nullable=True))
    op.add_column("feedbacks", sa.Column("score_fit", sa.Integer(), nullable=True))
    op.add_column("feedbacks", sa.Column("strengths", sa.Text(), nullable=True))
    op.add_column("feedbacks", sa.Column("weaknesses", sa.Text(), nullable=True))
    op.add_column("feedbacks", sa.Column("recommendation", sa.String(50), nullable=True))

    # Create status_history table
    op.create_table(
        "status_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50), nullable=False),
        sa.Column("changed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("changed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create documents table
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidate_profiles.id"), nullable=False),
        sa.Column("doc_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_table("status_history")
    op.drop_column("feedbacks", "recommendation")
    op.drop_column("feedbacks", "weaknesses")
    op.drop_column("feedbacks", "strengths")
    op.drop_column("feedbacks", "score_fit")
    op.drop_column("feedbacks", "score_communication")
    op.drop_column("feedbacks", "score_technical")
    op.drop_column("feedbacks", "score_overall")
    op.drop_column("interviews", "manager_id")
    op.drop_column("interviews", "comment")
    op.drop_column("interviews", "location")
    op.drop_column("interviews", "format")
    op.drop_column("candidate_profiles", "relocation_ready")
    op.drop_column("candidate_profiles", "work_format")
    op.drop_column("candidate_profiles", "employment_type")
    op.drop_column("candidate_profiles", "salary_to")
    op.drop_column("candidate_profiles", "salary_from")
    op.drop_column("candidate_profiles", "level")
    op.drop_column("candidate_profiles", "specialization")
    op.drop_column("candidate_profiles", "desired_position")
    op.drop_column("candidate_profiles", "portfolio")
    op.drop_column("candidate_profiles", "github")
    op.drop_column("candidate_profiles", "linkedin")
    op.drop_column("candidate_profiles", "birth_date")
    op.drop_column("candidate_profiles", "citizenship")
    op.drop_column("candidate_profiles", "city")
    op.drop_column("candidate_profiles", "phone")
