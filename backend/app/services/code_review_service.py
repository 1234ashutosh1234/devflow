from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import OrganizationRole
from app.repositories.code_review_repository import CodeReviewRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.pull_request_repository import PullRequestRepository
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.code_review import CodeReviewCreate


class CodeReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repository = CodeReviewRepository(db)
        self.pull_request_repository = PullRequestRepository(db)
        self.repository_repository = RepositoryRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def _get_pull_request_and_check_access(
        self,
        pull_request_id: int,
        user_id: int,
        minimum_role: OrganizationRole,
    ):
        pull_request = self.pull_request_repository.get_by_id(
            pull_request_id
        )

        if pull_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pull request not found",
            )

        repository = self.repository_repository.get_by_id(
            pull_request.repository_id
        )

        if repository is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository not found",
            )

        project = repository.project

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        membership = self.organization_repository.get_membership(
            organization_id=project.organization_id,
            user_id=user_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        try:
            user_role = OrganizationRole(membership.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid organization role",
            )

        role_levels = {
            OrganizationRole.VIEWER: 10,
            OrganizationRole.DEVELOPER: 20,
            OrganizationRole.ADMIN: 30,
            OrganizationRole.OWNER: 40,
        }

        if role_levels[user_role] < role_levels[minimum_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient organization permissions",
            )

        return pull_request

    def create(
        self,
        pull_request_id: int,
        user_id: int,
        data: CodeReviewCreate,
    ):
        pull_request = self._get_pull_request_and_check_access(
            pull_request_id=pull_request_id,
            user_id=user_id,
            minimum_role=OrganizationRole.DEVELOPER,
        )

        return self.review_repository.create(
            pull_request_id=pull_request.id,
            reviewer_id=user_id,
            status=data.status,
            summary=data.summary,
            score=data.score,
        )

    def list_by_pull_request(
        self,
        pull_request_id: int,
        user_id: int,
    ):
        self._get_pull_request_and_check_access(
            pull_request_id=pull_request_id,
            user_id=user_id,
            minimum_role=OrganizationRole.VIEWER,
        )

        return self.review_repository.get_by_pull_request(
            pull_request_id
        )

    def get_by_id(
        self,
        review_id: int,
        user_id: int,
    ):
        review = self.review_repository.get_by_id(review_id)

        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Code review not found",
            )

        self._get_pull_request_and_check_access(
            pull_request_id=review.pull_request_id,
            user_id=user_id,
            minimum_role=OrganizationRole.VIEWER,
        )

        return review