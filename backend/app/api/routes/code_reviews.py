from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.code_review import (
    CodeReviewCreate,
    CodeReviewResponse,
)
from app.services.code_review_service import CodeReviewService


router = APIRouter(
    prefix="/api/v1",
    tags=["Code Reviews"],
)


@router.post(
    "/pull-requests/{pull_request_id}/reviews",
    response_model=CodeReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_code_review(
    pull_request_id: int,
    data: CodeReviewCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = CodeReviewService(db)

    return service.create(
        pull_request_id=pull_request_id,
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "/pull-requests/{pull_request_id}/reviews",
    response_model=list[CodeReviewResponse],
)
def list_code_reviews(
    pull_request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = CodeReviewService(db)

    return service.list_by_pull_request(
        pull_request_id=pull_request_id,
        user_id=current_user.id,
    )


@router.get(
    "/code-reviews/{review_id}",
    response_model=CodeReviewResponse,
)
def get_code_review(
    review_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = CodeReviewService(db)

    return service.get_by_id(
        review_id=review_id,
        user_id=current_user.id,
    )