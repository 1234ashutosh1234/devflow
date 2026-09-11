from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CodeReview(Base):
    __tablename__ = "code_reviews"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    pull_request_id: Mapped[int] = mapped_column(
        ForeignKey(
            "pull_requests.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    reviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    pull_request = relationship(
        "PullRequest",
        back_populates="reviews",
    )

    reviewer = relationship(
        "User",
    )

    findings = relationship(
        "ReviewFinding",
        back_populates="code_review",
        cascade="all, delete-orphan",
    )