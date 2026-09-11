from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.ai_review import AIReviewRequest
from app.schemas.code_review import CodeReviewResponse
from app.schemas.review_finding import ReviewFindingResponse
from app.services.ai_review_service import AIReviewService


router = APIRouter(
    prefix="/api/v1",
    tags=["AI Code Review"],
)


@router.post(
    "/pull-requests/{pull_request_id}/ai-review",
    response_model=CodeReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_ai_review(
    pull_request_id: int,
    data: AIReviewRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = AIReviewService(db)

    return service.run_review(
        pull_request_id=pull_request_id,
        user_id=current_user.id,
        content=data.content,
        filename=data.filename,
    )


@router.get(
    "/code-reviews/{review_id}/findings",
    response_model=list[ReviewFindingResponse],
)
def list_ai_review_findings(
    review_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = AIReviewService(db)

    return service.list_findings(
        review_id=review_id,
        user_id=current_user.id,
    )