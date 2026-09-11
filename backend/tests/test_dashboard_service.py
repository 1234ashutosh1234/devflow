from datetime import datetime, timezone

from app.models.code_review import CodeReview
from app.models.organization import Organization, OrganizationMember
from app.models.project import Project
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_finding import ReviewFinding
from app.models.user import User
from app.services.dashboard_service import DashboardService


def test_dashboard_summary_is_scoped_to_user_organizations(
    db_session,
):
    user = User(
        email="dashboard@example.com",
        username="dashboard_user",
        hashed_password="test-hash",
    )
    db_session.add(user)
    db_session.flush()

    organization = Organization(
        name="Dashboard Org",
        slug="dashboard-org",
        owner_id=user.id,
    )
    db_session.add(organization)
    db_session.flush()

    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role="owner",
    )
    db_session.add(membership)

    project = Project(
        organization_id=organization.id,
        name="Dashboard Project",
        key="DB",
        created_by_id=user.id,
    )
    db_session.add(project)
    db_session.flush()

    repository = Repository(
        project_id=project.id,
        provider="github",
        external_id="example/devflow",
        clone_url="https://github.com/example/devflow.git",
        default_branch="main",
    )
    db_session.add(repository)
    db_session.flush()

    pull_request = PullRequest(
        repository_id=repository.id,
        external_number=1,
        title="Dashboard test PR",
        description="Test PR",
        author_id=user.id,
        source_branch="feature/test",
        target_branch="main",
        status="open",
    )
    db_session.add(pull_request)
    db_session.flush()

    review = CodeReview(
        pull_request_id=pull_request.id,
        reviewer_id=user.id,
        status="completed_with_findings",
        summary="Dashboard test review",
        score=80,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(review)
    db_session.flush()

    finding = ReviewFinding(
        code_review_id=review.id,
        filename="example.py",
        category="security",
        severity="high",
        title="Test finding",
        description="Test finding",
        line_number=10,
        suggestion="Fix the test finding",
        confidence=0.95,
    )
    db_session.add(finding)
    db_session.commit()

    result = DashboardService(db_session).get_summary(
        user_id=user.id
    )

    assert result.total_pull_requests == 1
    assert result.total_reviews == 1
    assert result.total_findings == 1
    assert result.average_score == 80.0

    assert len(result.recent_reviews) == 1
    assert result.recent_reviews[0].pull_request_number == 1
    assert result.recent_reviews[0].finding_count == 1
    assert result.recent_reviews[0].repository_name == "example/devflow"