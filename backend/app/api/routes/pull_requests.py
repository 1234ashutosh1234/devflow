from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.pull_request import (
    PullRequestCreate,
    PullRequestResponse,
)
from app.services.pull_request_service import PullRequestService


router = APIRouter(
    prefix="/api/v1",
    tags=["Pull Requests"],
)


@router.post(
    "/repositories/{repository_id}/pull-requests",
    response_model=PullRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pull_request(
    repository_id: int,
    data: PullRequestCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = PullRequestService(db)

    return service.create(
        repository_id=repository_id,
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "/repositories/{repository_id}/pull-requests",
    response_model=list[PullRequestResponse],
)
def list_pull_requests(
    repository_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = PullRequestService(db)

    return service.list_by_repository(
        repository_id=repository_id,
        user_id=current_user.id,
    )


@router.get(
    "/pull-requests/{pull_request_id}",
    response_model=PullRequestResponse,
)
def get_pull_request(
    pull_request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = PullRequestService(db)

    return service.get_by_id(
        pull_request_id=pull_request_id,
        user_id=current_user.id,
    )