from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.services.repository_service import RepositoryService


router = APIRouter(
    prefix="/api/v1",
    tags=["Repositories"],
)


@router.post(
    "/projects/{project_id}/repositories",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repository(
    project_id: int,
    data: RepositoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = RepositoryService(db)

    return service.create(
        project_id=project_id,
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "/projects/{project_id}/repositories",
    response_model=list[RepositoryResponse],
)
def list_repositories(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = RepositoryService(db)

    return service.list_by_project(
        project_id=project_id,
        user_id=current_user.id,
    )


@router.get(
    "/repositories/{repository_id}",
    response_model=RepositoryResponse,
)
def get_repository(
    repository_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = RepositoryService(db)

    return service.get_by_id(
        repository_id=repository_id,
        user_id=current_user.id,
    )