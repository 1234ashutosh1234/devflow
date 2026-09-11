from datetime import datetime, timezone

from app.schemas.dashboard import (
    DashboardReviewItem,
    DashboardSummaryResponse,
)


def test_dashboard_summary_defaults_to_empty_reviews():
    response = DashboardSummaryResponse(
        total_pull_requests=0,
        total_reviews=0,
        total_findings=0,
        average_score=None,
        recent_reviews=[],
    )

    assert response.total_pull_requests == 0
    assert response.total_reviews == 0
    assert response.total_findings == 0
    assert response.average_score is None
    assert response.recent_reviews == []


def test_dashboard_summary_contains_recent_review():
    review = DashboardReviewItem(
        review_id=10,
        pull_request_id=1,
        pull_request_number=1,
        pull_request_title="Improve code review workflow",
        project_name="Code Review Platform",
        repository_name="1234ashutosh1234/devflow",
        review_status="completed_with_findings",
        score=80,
        finding_count=2,
        created_at=datetime.now(timezone.utc),
    )

    response = DashboardSummaryResponse(
        total_pull_requests=1,
        total_reviews=1,
        total_findings=2,
        average_score=80.0,
        recent_reviews=[review],
    )

    assert response.recent_reviews[0].review_id == 10
    assert response.recent_reviews[0].finding_count == 2
    assert response.average_score == 80.0