"""Integration checks that run against the disposable CI PostgreSQL service.

The ordinary local/unit-test suite remains SQLite-backed. Set TEST_POSTGRES_URL
and apply Alembic migrations to enable these production-dialect checks.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, insert, select, text

from app.models.user import User


POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(
    not POSTGRES_URL,
    reason="TEST_POSTGRES_URL is not configured; PostgreSQL integration test skipped",
)


@pytest.fixture(scope="module")
def postgres_engine():
    if not POSTGRES_URL:
        pytest.skip("TEST_POSTGRES_URL is not configured")

    engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1
        yield engine
    finally:
        engine.dispose()


def test_postgres_schema_contains_application_tables(postgres_engine):
    tables = set(inspect(postgres_engine).get_table_names())
    expected = {
        "users",
        "organizations",
        "organization_members",
        "activity_logs",
        "projects",
        "repositories",
        "tasks",
        "pull_requests",
        "code_reviews",
        "review_findings",
        "alembic_version",
    }

    assert expected <= tables, f"Missing PostgreSQL tables: {sorted(expected - tables)}"


def test_postgres_schema_is_at_current_alembic_head(postgres_engine):
    config_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    alembic_config = Config(str(config_path))
    expected_revision = ScriptDirectory.from_config(alembic_config).get_current_head()

    with postgres_engine.connect() as connection:
        actual_revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()

    assert actual_revision == expected_revision


def test_postgres_user_insert_and_read_round_trip(postgres_engine):
    unique_id = uuid.uuid4().hex
    email = f"ci-{unique_id}@example.test"
    username = f"ci_{unique_id}"

    with postgres_engine.connect() as connection:
        transaction = connection.begin()
        try:
            inserted_id = connection.execute(
                insert(User.__table__).values(
                    email=email,
                    username=username,
                    hashed_password="ci-only-not-a-real-password-hash",
                    is_active=True,
                ).returning(User.id)
            ).scalar_one()

            stored_email = connection.execute(
                select(User.__table__.c.email).where(
                    User.__table__.c.id == inserted_id
                )
            ).scalar_one()

            assert stored_email == email
        finally:
            transaction.rollback()
