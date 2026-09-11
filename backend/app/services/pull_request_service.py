from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import OrganizationRole
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.pull_request_repository import PullRequestRepository
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.pull_request import PullRequestCreate


class PullRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.pull_request_repository = PullRequestRepository(db)
        self.repository_repository = RepositoryRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def _get_repository_and_check_access(
        self,
        repository_id: int,
        user_id: int,
        minimum_role: OrganizationRole,
    ):
        repository = self.repository_repository.get_by_id(repository_id)

        if repository is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository not found",
            )

        project = repository.project

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository project not found",
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

        return repository

    def create(
        self,
        repository_id: int,
        user_id: int,
        data: PullRequestCreate,
    ):
        repository = self._get_repository_and_check_access(
            repository_id=repository_id,
            user_id=user_id,
            minimum_role=OrganizationRole.DEVELOPER,
        )

        existing = self.pull_request_repository.get_by_external_number(
            repository_id=repository.id,
            external_number=data.external_number,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pull request with this number already exists",
            )

        return self.pull_request_repository.create(
            repository_id=repository.id,
            external_number=data.external_number,
            title=data.title,
            description=data.description,
            author_id=user_id,
            source_branch=data.source_branch,
            target_branch=data.target_branch,
            status=data.status,
        )

    def list_by_repository(
        self,
        repository_id: int,
        user_id: int,
    ):
        self._get_repository_and_check_access(
            repository_id=repository_id,
            user_id=user_id,
            minimum_role=OrganizationRole.VIEWER,
        )

        return self.pull_request_repository.get_by_repository(
            repository_id
        )

    def get_by_id(
        self,
        pull_request_id: int,
        user_id: int,
    ):
        pull_request = self.pull_request_repository.get_by_id(
            pull_request_id
        )

        if pull_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pull request not found",
            )

        self._get_repository_and_check_access(
            repository_id=pull_request.repository_id,
            user_id=user_id,
            minimum_role=OrganizationRole.VIEWER,
        )

        return pull_request