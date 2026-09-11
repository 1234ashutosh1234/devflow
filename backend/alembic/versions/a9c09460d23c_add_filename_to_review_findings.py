"""add filename to review findings

Revision ID: a9c09460d23c
Revises: b71e2f9c4a11
Create Date: 2026-09-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a9c09460d23c"
down_revision: Union[str, Sequence[str], None] = "b71e2f9c4a11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "review_findings",
        sa.Column(
            "filename",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_review_findings_filename",
        "review_findings",
        ["filename"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_review_findings_filename",
        table_name="review_findings",
    )

    op.drop_column(
        "review_findings",
        "filename",
    )