from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    require_organization_role,
)
from app.core.database import get_db
from app.core.permissions import OrganizationRole
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
)
from app.services.project_service import ProjectService


router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"],
)


@router.post(
    "/organizations/{organization_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    organization_id: int,
    data: ProjectCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    # Check that the current user has enough
    # permission to create a project.
    require_organization_role(
        organization_id=organization_id,
        user_id=current_user.id,
        minimum_role=OrganizationRole.DEVELOPER,
        db=db,
    )

    service = ProjectService(db)

    return service.create(
        organization_id=organization_id,
        data=data,
        user_id=current_user.id,
    )


@router.get(
    "/organizations/{organization_id}",
    response_model=list[ProjectResponse],
)
def list_projects(
    organization_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = ProjectService(db)

    return service.list_projects(
        organization_id=organization_id,
        user_id=current_user.id,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = ProjectService(db)

    return service.get_project(
        project_id=project_id,
        user_id=current_user.id,
    )