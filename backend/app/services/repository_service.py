from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import OrganizationRole
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.repository import RepositoryCreate


class RepositoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = RepositoryRepository(db)
        self.project_repository = ProjectRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def _get_project_and_check_access(
        self,
        project_id: int,
        user_id: int,
        minimum_role: OrganizationRole,
    ):
        project = self.project_repository.get_by_id(project_id)

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

        return project

    def create(
        self,
        project_id: int,
        user_id: int,
        data: RepositoryCreate,
    ):
        project = self._get_project_and_check_access(
            project_id=project_id,
            user_id=user_id,
            minimum_role=OrganizationRole.DEVELOPER,
        )

        if data.external_id:
            existing = self.repository.get_by_external_id(
                project_id=project.id,
                external_id=data.external_id,
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Repository with this external_id already exists",
                )

        return self.repository.create(
            project_id=project.id,
            provider=data.provider,
            external_id=data.external_id,
            clone_url=data.clone_url,
            default_branch=data.default_branch,
        )

    def list_by_project(
        self,
        project_id: int,
        user_id: int,
    ):
        self._get_project_and_check_access(
            project_id=project_id,
            user_id=user_id,
            minimum_role=OrganizationRole.VIEWER,
        )

        return self.repository.get_by_project(project_id)

    def get_by_id(
        self,
        repository_id: int,
        user_id: int,
    ):
        repository = self.repository.get_by_id(repository_id)

        if repository is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository not found",
            )

        self._get_project_and_check_access(
            project_id=repository.project_id,
            user_id=user_id,
            minimum_role=OrganizationRole.VIEWER,
        )

        return repository