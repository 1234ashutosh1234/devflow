from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.code_review import CodeReview
from app.models.organization import OrganizationMember
from app.models.project import Project
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_finding import ReviewFinding
from app.schemas.dashboard import (
    DashboardReviewItem,
    DashboardSummaryResponse,
)


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def _get_organization_ids(self, user_id: int) -> list[int]:
        statement = select(
            OrganizationMember.organization_id
        ).where(
            OrganizationMember.user_id == user_id
        )

        return list(self.db.scalars(statement).all())

    def get_summary(self, user_id: int) -> DashboardSummaryResponse:
        organization_ids = self._get_organization_ids(user_id)

        if not organization_ids:
            return DashboardSummaryResponse(
                total_pull_requests=0,
                total_reviews=0,
                total_findings=0,
                average_score=None,
                recent_reviews=[],
            )

        total_pull_requests = self.db.scalar(
            select(func.count(PullRequest.id))
            .join(
                Repository,
                PullRequest.repository_id == Repository.id,
            )
            .join(
                Project,
                Repository.project_id == Project.id,
            )
            .where(
                Project.organization_id.in_(organization_ids)
            )
        ) or 0

        total_reviews = self.db.scalar(
            select(func.count(CodeReview.id))
            .join(
                PullRequest,
                CodeReview.pull_request_id == PullRequest.id,
            )
            .join(
                Repository,
                PullRequest.repository_id == Repository.id,
            )
            .join(
                Project,
                Repository.project_id == Project.id,
            )
            .where(
                Project.organization_id.in_(organization_ids)
            )
        ) or 0

        total_findings = self.db.scalar(
            select(func.count(ReviewFinding.id))
            .join(
                CodeReview,
                ReviewFinding.code_review_id == CodeReview.id,
            )
            .join(
                PullRequest,
                CodeReview.pull_request_id == PullRequest.id,
            )
            .join(
                Repository,
                PullRequest.repository_id == Repository.id,
            )
            .join(
                Project,
                Repository.project_id == Project.id,
            )
            .where(
                Project.organization_id.in_(organization_ids)
            )
        ) or 0

        average_score = self.db.scalar(
            select(func.avg(CodeReview.score))
            .join(
                PullRequest,
                CodeReview.pull_request_id == PullRequest.id,
            )
            .join(
                Repository,
                PullRequest.repository_id == Repository.id,
            )
            .join(
                Project,
                Repository.project_id == Project.id,
            )
            .where(
                Project.organization_id.in_(organization_ids),
                CodeReview.score.is_not(None),
            )
        )

        recent_statement = (
            select(
                CodeReview.id,
                CodeReview.pull_request_id,
                PullRequest.external_number,
                PullRequest.title,
                Project.name.label("project_name"),
                Repository.external_id,
                CodeReview.status,
                CodeReview.score,
                CodeReview.created_at,
            )
            .join(
                PullRequest,
                CodeReview.pull_request_id == PullRequest.id,
            )
            .join(
                Repository,
                PullRequest.repository_id == Repository.id,
            )
            .join(
                Project,
                Repository.project_id == Project.id,
            )
            .where(
                Project.organization_id.in_(organization_ids)
            )
            .order_by(
                CodeReview.created_at.desc()
            )
            .limit(10)
        )

        recent_rows = self.db.execute(
            recent_statement
        ).all()

        review_ids = [row.id for row in recent_rows]

        finding_counts: dict[int, int] = {}

        if review_ids:
            finding_statement = (
                select(
                    ReviewFinding.code_review_id,
                    func.count(ReviewFinding.id),
                )
                .where(
                    ReviewFinding.code_review_id.in_(review_ids)
                )
                .group_by(
                    ReviewFinding.code_review_id
                )
            )

            finding_counts = {
                review_id: count
                for review_id, count in self.db.execute(
                    finding_statement
                ).all()
            }

        recent_reviews = [
            DashboardReviewItem(
                review_id=row.id,
                pull_request_id=row.pull_request_id,
                pull_request_number=row.external_number,
                pull_request_title=row.title,
                project_name=row.project_name,
                repository_name=row.external_id
                or "unknown",
                review_status=row.status,
                score=row.score,
                finding_count=finding_counts.get(row.id, 0),
                created_at=row.created_at,
            )
            for row in recent_rows
        ]

        normalized_average = (
            round(float(average_score), 2)
            if average_score is not None
            else None
        )

        return DashboardSummaryResponse(
            total_pull_requests=int(total_pull_requests),
            total_reviews=int(total_reviews),
            total_findings=int(total_findings),
            average_score=normalized_average,
            recent_reviews=recent_reviews,
        )