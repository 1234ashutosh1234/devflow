from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "external_id",
            name="uq_repositories_project_external_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    clone_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    default_branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="main",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="repository",
    )

    pull_requests = relationship(
        "PullRequest",
        back_populates="repository",
        cascade="all, delete-orphan",
    )