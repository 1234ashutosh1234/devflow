from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.code_review import CodeReview
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_finding import ReviewFinding
from app.models.user import User
from app.services.github_review_publisher import GitHubReviewPublisher


router = APIRouter(
    prefix="/api/v1/github",
    tags=["GitHub"],
)


@router.post(
    "/reviews/{review_id}/publish",
    status_code=status.HTTP_200_OK,
)
def publish_github_review(
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
    review = db.get(CodeReview, review_id)

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Code review {review_id} not found.",
        )

    pull_request = db.get(
        PullRequest,
        review.pull_request_id,
    )

    if pull_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pull request associated with the review was not found.",
        )

    repository = db.get(
        Repository,
        pull_request.repository_id,
    )

    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository associated with the pull request was not found.",
        )

    findings = list(
        db.scalars(
            select(ReviewFinding)
            .where(
                ReviewFinding.code_review_id == review.id
            )
            .order_by(
                ReviewFinding.severity.desc(),
                ReviewFinding.line_number.asc(),
                ReviewFinding.id.asc(),
            )
        ).all()
    )

    publisher = GitHubReviewPublisher(db)

    try:
        result = publisher.publish(
            review=review,
            pull_request=pull_request,
            repository=repository,
            findings=findings,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
     raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=str(exc),
    ) from exc


    return {
        "published_by": current_user.username,
        **result,
    }