"""add review findings table

Revision ID: b71e2f9c4a11
Revises: 31e8cf0f275b
Create Date: 2026-09-06 22:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b71e2f9c4a11"
down_revision: Union[str, Sequence[str], None] = "31e8cf0f275b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "review_findings",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "code_review_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "line_number",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "suggestion",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "confidence",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["code_review_id"],
            ["code_reviews.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_review_findings_id",
        "review_findings",
        ["id"],
    )

    op.create_index(
        "ix_review_findings_code_review_id",
        "review_findings",
        ["code_review_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_review_findings_code_review_id",
        table_name="review_findings",
    )

    op.drop_index(
        "ix_review_findings_id",
        table_name="review_findings",
    )

    op.drop_table("review_findings")