import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base

# Import all models so SQLAlchemy registers every table.
from app.models.activity_log import ActivityLog
from app.models.code_review import CodeReview
from app.models.organization import Organization, OrganizationMember
from app.models.project import Project
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_finding import ReviewFinding
from app.models.task import Task
from app.models.user import User


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session: Session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()