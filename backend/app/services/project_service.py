from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.project_repository import (
    ProjectRepository,
)
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, db: Session):
        self.project_repository = ProjectRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def create(
        self,
        organization_id: int,
        data: ProjectCreate,
        user_id: int,
    ):
        membership = (
            self.organization_repository.get_membership(
                organization_id,
                user_id,
            )
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        existing = self.project_repository.get_by_key(
            organization_id,
            data.key.upper(),
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project key already exists in this organization",
            )

        return self.project_repository.create(
            organization_id=organization_id,
            name=data.name,
            key=data.key.upper(),
            description=data.description,
            created_by_id=user_id,
        )

    def list_projects(
        self,
        organization_id: int,
        user_id: int,
    ):
        membership = (
            self.organization_repository.get_membership(
                organization_id,
                user_id,
            )
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        return self.project_repository.get_by_organization(
            organization_id
        )

    def get_project(
        self,
        project_id: int,
        user_id: int,
    ):
        project = self.project_repository.get_by_id(
            project_id
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        membership = (
            self.organization_repository.get_membership(
                project.organization_id,
                user_id,
            )
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        return project